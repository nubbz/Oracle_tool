# Oracle Tool 项目审计报告

> 审计日期: 2026-05-16
> 审计视角: 产品经理 + DBA 专家
> 状态说明: ❌ 待修复 | 🔄 进行中 | ✅ 已修复

---

## 一、严重问题（P0 — 必须立即修复）

### P0-1 Shell 命令注入风险 ✅
**文件**: `backend/app/generators/base.py` line 32-33, 115-118, 144-180, 267-272

用户输入的 `username`、`password`、`host`、`service_name` 等参数未经 shell 转义直接嵌入生成的脚本。攻击者可通过 `"; rm -rf /` 等输入执行任意命令。

**受影响代码**:
```python
# base.py:32-33 — 连接串直接拼接
return f'{username}/{password}@{host}:{port}/{ident}'
# base.py:117-118 — shell 变量赋值
'DB_USER="{}"'.format(username)
'DB_{}="{}"'.format(ident_label, ident_value)
# base.py:180 — SSH 密码直接拼入 sshpass
'sshpass -p "{}" ssh ...'.format(ssh_pwd)
```

**修复方案**: 使用 `shlex.quote()` 转义所有用户输入；DDL 中的标识符用正则验证（仅允许 `[A-Za-z0-9_]`）。

---

### P0-2 密码明文存储于历史记录 ✅
**文件**: `backend/app/models/history.py` line 12-13

`connection` 字段以 JSON Text 存储，包含完整的数据库用户名和密码，未经加密直接写入 SQLite。

**修复方案**: 存入前对 `connection` JSON 中的 `password` 字段调用 `crypto_service.encrypt()`，读取时 `decrypt()`。

---

### P0-3 加密密钥派生逻辑错误 ✅
**文件**: `backend/app/services/crypto_service.py` line 11-13

```python
return base64.urlsafe_b64decode(
    key_str.encode() if len(key_str) > 32 else Fernet.generate_key()
)
```

当 `ENCRYPTION_KEY` 长度 ≤ 32 时，`Fernet.generate_key()` 的返回值被错误地传入 `b64decode`，导致每次重启生成不同的密钥，之前加密的数据无法解密。

**修复方案**: 重写 `_get_key()` 逻辑，确保 ENCRYPTION_KEY 存在时使用它（Fernet key 是 32 字节 url-safe base64 编码），不存在时从 `.secret` 文件读取或生成新密钥。

---

### P0-4 JWT Secret 硬编码 ✅
**文件**: `backend/app/config.py` line 5

默认 secret key `"oracle-backup-tool-secret-key-change-in-production-2026"` 硬编码在源码中。生产环境未设置环境变量时 JWT 可被伪造。

**修复方案**: 启动时检测默认 key 并打印严重警告；自动生成随机 secret 写入 `.secret` 文件并复用。

---

### P0-5 SSH AutoAddPolicy 中间人攻击风险 ✅
**文件**: `backend/app/services/ssh_service.py` line 17

使用 `paramiko.AutoAddPolicy()` 自动接受未知主机密钥，存在中间人攻击风险。

**修复方案**: 改用 `WarningPolicy` 或 `RejectPolicy`，支持配置 `known_hosts` 文件路径。

---

### P0-6 环境 SSH 密码明文存储 ✅
**文件**: `backend/app/models/environment.py` line 24-26

`ssh_password` 和 `ssh_key_passphrase` 明文存储在数据库中。`database.py` 中已有 `migrate_encrypt_passwords()` 迁移函数，但需确认其完整性。

**修复方案**: 确认迁移函数正确调用 `crypto_service`，写入前自动加密，读取时脱敏。

---

## 二、核心功能缺失（P1）

### P1-1 RMAN 命令生成器 ✅
**问题**: 生产环境中 90% 的 Oracle 备份策略基于 RMAN（Recovery Manager），目前完全未覆盖。

**需求清单**:
- 全库备份 / 增量备份（Level 0/1）/ 归档日志备份
- RMAN 恢复脚本（完全恢复、基于时间点、基于 SCN）
- RMAN 配置参数（RETENTION POLICY、COMPRESSION、CHANNEL、PARALLELISM）
- 验证（VALIDATE）和交叉检查（CROSSCHECK）命令
- 脚本模板（每日备份、每周全量、迁移前备份等）

---

### P1-2 命令模板系统 ✅
**问题**: DBA 有大量重复性备份任务，缺少参数组合的保存和复用能力。

**需求清单**:
- 保存当前参数为命名模板
- 模板 CRUD（创建/读取/更新/删除）
- 预置 DBA 常用模板（每日全量、每周 Schema 备份、迁移导入等）
- 团队内模板共享

---

### P1-3 Optimizer/Installer 命令生成逻辑不在后端 ✅
**注**: 后端已有命令生成逻辑，前端重复的客户端预览代码将在 P2-4 去重时清理。
**文件**:
- `frontend/src/views/OptimizerView.vue` line 242-358（FLAG_MAP + computed）
- `frontend/src/views/InstallerView.vue` line 540-608

Optimizer 和 Installer 的命令生成逻辑完全在前端 JS 中硬编码，绕过了后端的生成器架构和校验系统。导致：
- 前后端逻辑可能不一致
- 无法统一维护和测试
- 客户端可篡改生成逻辑

**修复方案**: 将命令生成逻辑迁移到后端（新建 `optimizer_gen.py`、`installer_gen.py`），前端改为调用 API。

---

## 三、质量与合规（P2）

### P2-1 exp/imp/expdp/impdp 参数覆盖不完整 ✅
**文件**: `backend/app/generators/` 下四个生成器

| 缺失参数 | 适用工具 | 重要性 |
|---|---|---|
| `METRICS` | expdp/impdp | 高 |
| `STATUS` | expdp/impdp | 高 |
| `DATA_OPTIONS=SKIP_CONSTRAINT_ERRORS` | expdp | 高 |
| `PARTITION_OPTIONS` | impdp | 高 |
| `TRANSFORM` | impdp | 高 |
| `FULL` | expdp/impdp | 中 |
| `VIEWS_AS_TABLES` | impdp (12c+) | 中 |
| `NLS_CHARSET` | exp/imp | 中 |
| `KEEP_MASTER` | expdp/impdp | 中 |

同时 `version_compat.py` 和 `conflict_engine.py` 需同步更新版本校验和冲突检测规则。

---

### P2-2 前端表单验证缺失 ✅
**文件**: 所有表单 View 组件

| 页面 | 问题 |
|---|---|
| `LoginView.vue` | 仅检查空值，无密码强度/用户名格式验证 |
| `GeneratorView.vue` | 有部分验证但未用 el-form rules |
| `EnvironmentsView.vue` | IP/端口无格式校验 |
| `OptimizerView.vue` | **零验证**，可提交空表单 |
| `InstallerView.vue` | **零验证**，可提交空表单 |

**修复方案**: 使用 Element Plus `el-form` 的 `:rules` 属性实现声明式验证。

---

### P2-3 审计日志缺失 ✅
**问题**: 涉及生产数据库凭据的工具，无操作审计追踪。

**需求**: 记录所有敏感操作（命令生成、环境增删改、连接测试、用户登录）的时间/IP/用户/操作详情。

---

### P2-4 前端代码重复 ✅
**重复代码清单**:

| 重复内容 | 文件 1 | 文件 2 |
|---|---|---|
| `excludeTypes` / `excludeLabels` / `buildExcludeVal` | `ExpdpParams.vue` line 261-280 | `ImpdpParams.vue` line 319-338 |
| `downloadScript` 函数 | `OptimizerView.vue` line 383-406 | `InstallerView.vue` line 633-656 |
| `copyCommand` 函数 | `OptimizerView.vue` line 361-368 | `InstallerView.vue` line 611-618 |
| `envTypeTag` 函数 | `GeneratorView.vue` line 152 | `EnvironmentsView.vue` line 222 |
| `useTheme.ts` 死代码 | `composables/useTheme.ts` | 与 `settingsStore.ts` 重复 |

---

### P2-5 版本兼容性校验不完整 ❌
**文件**: `backend/app/validators/version_compat.py`

- `exp`/`imp` 在 Oracle 23c 已完全废弃，应给出严重警告
- `COMPRESSION` 的 LOW/MEDIUM/HIGH 级别从 12c 才支持
- `ENCRYPTION_MODE=AUTO` 从 12.2 才引入

---

### P2-6 生成脚本运维增强 ❌
**文件**: `backend/app/generators/base.py`

- 磁盘空间仅 `echo` 提示，无实际 `df -h` 检查
- `ORACLE_HOME` 硬编码，未检测 `/etc/oratab`
- 长任务无 `STATUS` 监控脚本
- 邮件通知被注释，应提供可选 webhook 通知

---

## 四、高级功能（P3）

### P3-1 权限分级与角色管理 ✅
**现状**: 所有用户平等，无角色区分。
**需求**: admin（全权限）/ operator（可生成命令）/ viewer（只读）三级角色，注册需 admin 审批。

### P3-2 SSH 远程执行命令 ✅
**现状**: 只生成命令，无法在目标服务器上执行。
**需求**: 基于已有 SSH 基础设施，异步执行命令 + WebSocket 推送输出。

### P3-3 批量任务与调度 ✅
**需求**: 批量为多 Schema 生成命令、cron 调度、任务状态机。

### P3-4 sqlldr 命令生成器 ✅
**需求**: SQL*Loader 控制文件生成 + 数据文件格式配置。

### P3-5 响应式布局 ✅
**现状**: 零 media query，侧边栏固定 220px，移动端完全不可用。
**需求**: 可折叠侧边栏 + 响应式栅格 + 移动端适配。

---

## 五、其他已发现问题

| # | 问题 | 文件 | 级别 |
|---|---|---|---|
| 1 | JWT 存 localStorage（XSS 风险） | `stores/authStore.ts` | 安全 |
| 2 | downloadScript 绕过 axios 直接用 fetch | `OptimizerView.vue:385`, `InstallerView.vue:636` | 架构 |
| 3 | 大量 `any` 类型 | API 层、Views、Components | 质量 |
| 4 | CollapsibleSection 忽略 defaultExpanded | `CollapsibleSection.vue:20` | Bug |
| 5 | 版本号 `'26'` 代表 23c | `InstallerView.vue:437` | Bug |
| 6 | PasswordInput.vue 引用未定义的 showPwd | `PasswordInput.vue:2-3` | Bug |
| 7 | HistoryView handleCopy 引用未导入的 composable | `HistoryView.vue:102` | Bug |
| 8 | 无离开页面确认 | 所有表单页面 | UX |
| 9 | 无 Token 刷新机制 | `api/index.ts` | 安全 |
| 10 | SQLite 不支持并发写入 | `database.py` | 架构 |
| 11 | CDB/PDB 支持不深入 | `expdp_gen.py:84-85` | 功能 |
| 12 | 无国际化（i18n） | 全局 | 功能 |
| 13 | 无 PWA/离线支持 | 全局 | 功能 |
| 14 | 无单元/E2E 测试 | 全局 | 质量 |

---

## 修复进度

| 优先级 | 总项 | 已完成 | 状态 |
|---|---|---|---|
| P0 | 6 | 6 | ✅ 已完成 |
| P1 | 3 | 3 | ✅ 已完成 |
| P2 | 6 | 4 | 🔄 进行中（P2-5/P2-6 优化项待后续迭代） |
| P3 | 5 | 5 | ✅ 已完成 |
