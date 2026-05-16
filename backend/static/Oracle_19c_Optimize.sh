#!/bin/bash
#==============================================================#
#                   Oracle 19c 数据库参数优化脚本                   #
#==============================================================#
# 使用方法:
#   chmod +x Oracle_19c_Optimize.sh
#   ./Oracle_19c_Optimize.sh [选项] [参数]
#
# 快速示例:
#   ./Oracle_19c_Optimize.sh                                     # 使用脚本内默认变量，执行全部步骤
#   ./Oracle_19c_Optimize.sh -d orcl -m single                  # 指定数据库和单实例模式，执行全部步骤
#   ./Oracle_19c_Optimize.sh -d orcl -s omf,redolog,para        # 只执行 OMF、redo 日志、参数优化
#   ./Oracle_19c_Optimize.sh -d orcl -r 1024 -p 3000           # 指定 redo 大小和 processes 值
#   ./Oracle_19c_Optimize.sh -h                                 # 查看完整帮助
#==============================================================#

oracleinstalllog="/tmp/oracle_optimize_$(date +%Y%m%d_%H%M%S).log"

#==============================================================#
#                      默认变量配置                               #
#==============================================================#
oracle_user=oracle
db_name=orcl
iscdb=false
pdbname=pdb01
oracle_install_mode=rac
restart_after=false
redosize=2048
processes=3000
open_cursors=1500
session_cached_cursors=300
undo_retention=10800
parallel_max_servers=64
db_files=5000
sga_target=""
pga_target=""
db_memory=""
data_asm_group=DATA
arch_asm_group=ARCH
oradata_dir=/oradata
archive_dir=/oradata/arch
env_oracle_home=/u01/app/oracle/product/19.3.0/db
env_grid_home=/u01/app/19.3.0/grid
backup_dir=/backup
os_type=rhel
current=$(date +%Y%m%d%H%M%S)

#==============================================================#
#                      命令行参数解析                              #
#==============================================================#

function usage() {
  cat <<'USAGE'
Oracle 19c 数据库参数优化脚本
============================

用法: ./Oracle_19c_Optimize.sh [选项] [参数]

【通用选项】
  -h                显示帮助信息
  -d <db_name>      数据库实例名（默认: orcl）
  -m <mode>         安装模式: rac / standalone / single（默认: rac）
  -s <steps>        指定执行的步骤，逗号分隔（默认: all，即全部执行）

【变量选项】
  -u <user>         Oracle 用户名（默认: oracle）
  -o <oracle_home>  Oracle Home 路径
  -g <grid_home>    Grid Home 路径
  -r <size_mb>      重做日志大小 MB（默认: 2048）
  -p <num>          processes 值（默认: 3000）
  -c <num>          open_cursors 值（默认: 1500）
  -P <num>          session_cached_cursors 值（默认: 300）
  -R <num>          parallel_max_servers 值（默认: 64）
  -U <num>          undo_retention 秒数（默认: 10800）
  -F <num>          db_files 值（默认: 5000）
  -M <size>M|G      指定数据库总内存，自动按 SGA:PGA=80:20 分配
  -S <size>M|G      手动指定 SGA_TARGET（优先级高于 -M）
  -G <size>M|G      手动指定 PGA_AGGREGATE_TARGET（优先级高于 -M）
  -A <diskgroup>    ASM 数据磁盘组名（默认: DATA）
  -a <diskgroup>    ASM 归档磁盘组名（默认: ARCH）
  -b <dir>          备份目录（默认: /backup）
  -D <dir>          文件系统数据目录（single 模式，默认: /oradata）
  -z                优化完成后重启数据库（执行前需确认）

【可选步骤列表】
  omf       配置 OMF 和归档日志路径
  redolog   配置在线重做日志（自动识别 RAC/单实例）
  backup    配置 RMAN 备份脚本和定时任务
  para      优化数据库核心参数（含 RAC 专属、密码策略、优化器参数等）
  sqlnet    配置 sqlnet.ora（19c 独有）
  glogin    配置 glogin.sql

【使用示例】
  # 使用全部默认值，执行所有步骤
  ./Oracle_19c_Optimize.sh

  # 指定数据库实例名和单实例模式
  ./Oracle_19c_Optimize.sh -d orcl -m single

  # 只优化数据库参数（不修改 redo、备份等）
  ./Oracle_19c_Optimize.sh -d orcl -s para

  # 只添加 redo 日志 + 优化参数
  ./Oracle_19c_Optimize.sh -d orcl -s redolog,para

  # 指定自定义参数值
  ./Oracle_19c_Optimize.sh -d orcl -r 4096 -p 5000 -c 2000

  # 手动指定 SGA/PGA
  ./Oracle_19c_Optimize.sh -d orcl -S 16G -G 4G

  # 指定数据库总内存，自动按 SGA:PGA=80:20 分配
  ./Oracle_19c_Optimize.sh -d orcl -M 64G

  # RAC 环境指定 ASM 磁盘组
  ./Oracle_19c_Optimize.sh -d zjyyhis -m rac -A DATA -a ARCH -s redolog,para

  # 优化完成后重启数据库
  ./Oracle_19c_Optimize.sh -d orcl -z

  # 查看帮助
  ./Oracle_19c_Optimize.sh -h

  # 打印当前默认变量值
  ./Oracle_19c_Optimize.sh --defaults

【日志】
  执行日志同时输出到屏幕和文件: /tmp/oracle_optimize_YYYYMMDD_HHMMSS.log
USAGE
  exit 0
}

# 打印当前默认变量值
function print_defaults() {
  echo "Oracle 19c 数据库参数优化脚本 - 当前默认变量值"
  echo "=================================================="
  printf "  %-35s %s\n" "db_name (数据库实例名)"         "$db_name"
  printf "  %-35s %s\n" "oracle_install_mode (安装模式)" "$oracle_install_mode"
  printf "  %-35s %s\n" "oracle_user (Oracle用户)"       "$oracle_user"
  printf "  %-35s %s\n" "env_oracle_home (Oracle Home)"  "$env_oracle_home"
  printf "  %-35s %s\n" "env_grid_home (Grid Home)"      "$env_grid_home"
  printf "  %-35s %s\n" "redosize (重做日志 MB)"         "$redosize"
  printf "  %-35s %s\n" "processes"                       "$processes"
  printf "  %-35s %s\n" "open_cursors"                    "$open_cursors"
  printf "  %-35s %s\n" "session_cached_cursors"          "$session_cached_cursors"
  printf "  %-35s %s\n" "undo_retention"                  "$undo_retention"
  printf "  %-35s %s\n" "parallel_max_servers"            "$parallel_max_servers"
  printf "  %-35s %s\n" "undo_retention"                  "$undo_retention"
  printf "  %-35s %s\n" "db_files"                        "$db_files"
  printf "  %-35s %s\n" "db_memory (数据库总内存)"        "${db_memory:-自动计算}"
  printf "  %-35s %s\n" "sga_target (SGA大小)"            "${sga_target:-自动计算}"
  printf "  %-35s %s\n" "pga_target (PGA大小)"            "${pga_target:-自动计算}"
  printf "  %-35s %s\n" "db_files"                        "$db_files"
  printf "  %-35s %s\n" "data_asm_group (ASM数据磁盘组)" "$data_asm_group"
  printf "  %-35s %s\n" "arch_asm_group (ASM归档磁盘组)" "$arch_asm_group"
  printf "  %-35s %s\n" "oradata_dir (数据目录)"         "$oradata_dir"
  printf "  %-35s %s\n" "archive_dir (归档目录)"         "$archive_dir"
  printf "  %-35s %s\n" "backup_dir (备份目录)"          "$backup_dir"
  printf "  %-35s %s\n" "os_type (系统类型)"             "$os_type"
  echo "=================================================="
  exit 0
}

# 解析参数
ENABLED_STEPS=""
# 先处理 --defaults（不在 getopts 范围内）
if [[ "$1" == "--defaults" ]]; then
  print_defaults
fi
while getopts ":hd:m:s:u:o:g:r:p:c:P:R:U:F:M:S:G:A:a:b:D:z" opt; do
  case $opt in
    h) usage ;;
    d) db_name="$OPTARG" ;;
    m) oracle_install_mode="$OPTARG" ;;
    s) ENABLED_STEPS="$OPTARG" ;;
    u) oracle_user="$OPTARG" ;;
    o) env_oracle_home="$OPTARG" ;;
    g) env_grid_home="$OPTARG" ;;
    r) redosize="$OPTARG" ;;
    p) processes="$OPTARG" ;;
    c) open_cursors="$OPTARG" ;;
    P) session_cached_cursors="$OPTARG" ;;
    R) parallel_max_servers="$OPTARG" ;;
    U) undo_retention="$OPTARG" ;;
    F) db_files="$OPTARG" ;;
    M) db_memory="$OPTARG" ;;
    S) sga_target="$OPTARG" ;;
    G) pga_target="$OPTARG" ;;
    A) data_asm_group="$OPTARG" ;;
    a) arch_asm_group="$OPTARG" ;;
    b) backup_dir="$OPTARG" ;;
    D) oradata_dir="$OPTARG" ;;
    z) restart_after=true ;;
    :)
      echo "错误: 选项 -$OPTARG 需要参数"
      usage
      ;;
    ?)
      echo "错误: 未知选项 -$OPTARG"
      usage
      ;;
  esac
done

#==============================================================#
#                  写入日志（必须在参数解析之后）                    #
#==============================================================#
exec > >(tee -a "$oracleinstalllog") 2>&1

#==============================================================#
#                     步骤控制函数                                #
#==============================================================

# 检查某个步骤是否启用
function should_run() {
  local step=$1
  if [[ -z "$ENABLED_STEPS" || "$ENABLED_STEPS" == "all" ]]; then
    return 0
  fi
  # 将逗号分隔转为换行，逐行匹配
  echo "$ENABLED_STEPS" | tr ',' '\n' | grep -qx "$step"
  return $?
}

# 打印用户选择的步骤
function print_enabled_steps() {
  if [[ -z "$ENABLED_STEPS" || "$ENABLED_STEPS" == "all" ]]; then
    step_log "执行步骤: 全部 (all)"
  else
    step_log "执行步骤: $ENABLED_STEPS"
  fi
  # 打印跳过的步骤
  local all_steps="omf redolog backup para sqlnet glogin"
  for s in $all_steps; do
    if ! should_run "$s"; then
      step_log "跳过步骤: $s"
    fi
  done
}

#==============================================================#
#                     RAC IP 解析（兼容传参）                     #
#==============================================================#
# rac_public_ips 数组：如果用户在脚本内硬编码则使用，否则尝试从 hosts 解析
if [[ ${#rac_public_ips[@]} -eq 0 ]]; then
  # 尝试从 /etc/hosts 解析节点 IP（需要配置 rac_nodes 变量）
  if [[ -n "$rac_nodes" ]]; then
    rac_public_ips=()
    for node in $rac_nodes; do
      ip=$(grep -w "$node" /etc/hosts | awk '{print $1}' | head -1)
      if [[ -n "$ip" ]]; then
        rac_public_ips+=("$ip")
      fi
    done
  fi
fi

#==============================================================#
#                        辅助函数定义                             #
#==============================================================#

# 颜色打印
function color_printf() {
  declare -u con_flag
  declare -A color_map=(
    ["red"]='\E[1;31m'
    ["green"]='\E[1;32m'
    ["blue"]='\E[1;34m'
    ["yellow"]='\E[1;33m'
    ["light_blue"]='\E[1;94m'
    ["purple"]='\033[35m'
  )
  local res='\E[0m' default_color='\E[1;32m'
  local color=${color_map[$1]:-"$default_color"}
  case "$1" in
  "red")
    printf "\n${color}%-20s %-30s %-50s\n${res}\n" "$2" "$3" "$4"
    exit 1
    ;;
  "green" | "light_blue")
    printf "${color}%-20s %-30s %-50s\n${res}" "$2" "$3" "$4"
    ;;
  "blue" | "yellow" | "purple")
    printf "\n${color}%-20s %-30s %-50s\n${res}" "$2" "$3" "$4"
    ;;
  esac
}

# 日志打印（标题）
function log_print() {
  echo
  color_printf green "#==============================================================#"
  color_printf green "$1"
  color_printf green "#==============================================================#"
  echo
}

# 步骤日志（带时间戳）
function step_log() {
  local ts
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[${ts}] $1"
}

# 步骤结果日志
function step_result() {
  local ts rc=$?
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  if ((rc == 0)); then
    echo "[${ts}] $1 => 成功"
  else
    echo "[${ts}] $1 => 失败 (返回码: ${rc})"
  fi
}

# 检查文件是否存在
function check_file() {
  if [[ -e "$1" ]]; then return 0; else return 1; fi
}

# 删除文件
function rm_file() {
  local file=$1
  if check_file "$file"; then
    /bin/rm -rf "$file" >/dev/null 2>&1
  fi
}

# 备份恢复文件
function backup_restore_file() {
  local file_path=$1
  step_log "备份文件: $file_path"
  if check_file "$file_path"; then
    if (($(grep -E -c "# OracleBegin" "$file_path") == 0)); then
      /bin/cp -f "$file_path"{,.original}
      step_log "首次修改，备份为 ${file_path}.original"
    else
      /bin/cp -f "$file_path"{,."$current"}
      /bin/cp -f "$file_path"{.original,}
      step_log "已有 OracleBegin 标记，备份为 ${file_path}.${current} 并还原 .original"
    fi
  else
    touch "$file_path".original
    step_log "文件不存在，创建空 ${file_path}.original"
  fi
  step_result "备份文件 $file_path"
}

# 写入文件
function write_file() {
  local flag=$1 file_name=$2 content=$3
  if [[ $flag == "Y" ]]; then
    cat <<-EOF >"$file_name"
			$content
		EOF
    step_log "覆盖写入文件: $file_name"
  elif [[ $flag == "N" ]]; then
    cat <<-EOF >>"$file_name"
			$content
		EOF
    step_log "追加写入文件: $file_name"
  fi
}

# 以 oracle 用户执行命令
function run_as_oracle() {
  local command="$1"
  step_log "run_as_oracle: $command"
  su - $oracle_user -c "bash -l -c \"$command\""
  step_result "run_as_oracle"
}

# 执行 sqlplus（带日志）
function execute_sqlplus() {
  local dbname="$1" format="$2" sql="$3"
  step_log "execute_sqlplus [dbname=$dbname]: $sql" >&2

  # === ORACLE_SID 自动探测（在 su - 外部执行，避免 heredoc 转义问题）===
  local detected_sid=""

  echo "[SID探测] Step0: pmon进程列表:" >&2
  ps -ef 2>/dev/null | grep -E "_pmon" | grep -v grep >&2
  echo "[SID探测] Step0: /etc/oratab 内容:" >&2
  cat /etc/oratab 2>/dev/null >&2
  echo "[SID探测] Step0: 传入 dbname=$dbname" >&2

  detected_sid=$(ps -ef 2>/dev/null | grep -E "[o]ra_pmon_${dbname}[0-9]* " | head -1 | sed 's/.*ora_pmon_//;s/ .*//')
  echo "[SID探测] Step1 精确pmon(ora_pmon_格式): detected_sid=$detected_sid" >&2

  if [[ -z "$detected_sid" ]]; then
    detected_sid=$(ps -ef 2>/dev/null | grep -E "[o]ra_${dbname}[0-9]*_pmon" | head -1 | sed 's/.*ora_//;s/_pmon.*//')
    echo "[SID探测] Step2 精确pmon(ora_SID_pmon格式): detected_sid=$detected_sid" >&2
  fi

  if [[ -z "$detected_sid" ]]; then
    detected_sid=$(ps -ef 2>/dev/null | grep -E "[o]ra_pmon_" | grep -i "${dbname}" | head -1 | sed 's/.*ora_pmon_//;s/ .*//')
    echo "[SID探测] Step3 宽松pmon: detected_sid=$detected_sid" >&2
  fi

  if [[ -z "$detected_sid" && -f /etc/oratab ]]; then
    detected_sid=$(grep -iE "^${dbname}[0-9]*:" /etc/oratab | head -1 | cut -d: -f1)
    echo "[SID探测] Step4 oratab: detected_sid=$detected_sid" >&2
  fi

  if [[ -z "$detected_sid" ]]; then
    detected_sid=$(srvctl status database -d $dbname 2>/dev/null | grep -i "is running" | head -1 | awk '{print $2}')
    echo "[SID探测] Step5 srvctl: detected_sid=$detected_sid" >&2
  fi

  if [[ -n "$detected_sid" ]]; then
    step_log "INFO: 自动探测到本节点实例 ORACLE_SID=$detected_sid" >&2
  elif [[ -f /home/$oracle_user/.$dbname ]]; then
    detected_sid=$dbname
    step_log "INFO: 使用环境文件 /home/$oracle_user/.$dbname" >&2
  else
    detected_sid=$dbname
    step_log "WARNING: 无法探测实例名且环境文件不存在，使用 ORACLE_SID=$dbname" >&2
  fi

  # === 执行 sqlplus ===
  local output
  output=$(su - $oracle_user <<-SOF
		export ORACLE_SID=$detected_sid
		[[ -f /home/$oracle_user/.$detected_sid ]] && source /home/$oracle_user/.$detected_sid
		sqlplus -S / as sysdba<<'EOF'
		set lin 2222 pages 1000 tab off feedback off
		$format
		$sql
		exit;
		EOF
	SOF
  )
  local rc=$?
  echo "$output"
  if ((rc != 0)); then
    step_log "sqlplus 返回码: $rc" >&2
  fi
  return $rc
}
# 安装软件包
function install_package() {
  local yum_cmd
  case "$os_type" in
  "sles")     yum_cmd=zypper ;;
  "ubuntu" | "debian" | "Deepin") yum_cmd=apt-get ;;
  *)          yum_cmd=yum ;;
  esac
  for package in "$@"; do
    step_log "安装软件包: $yum_cmd install -y $package"
    $yum_cmd install -y "$package" 2>&1
    step_result "安装 $package"
  done
}

#==============================================================#
#                    步骤: 配置 OMF 以及归档                      #
#==============================================================#
function conf_omf() {
  log_print "配置 OMF 和归档日志路径"
  local omf dbname=$1 arch

  if [[ "$oracle_install_mode" =~ ^(rac|standalone)$ ]]; then
    omf=+$data_asm_group
    arch=+$arch_asm_group
    step_log "ASM 模式: omf=$omf, arch=$arch"
    step_log "配置 RMAN snapshot controlfile name: $omf/snapcf_$dbname.f"
    su - $oracle_user <<-SO
			source /home/$oracle_user/.$dbname
			rman target / <<-EOF
			CONFIGURE SNAPSHOT CONTROLFILE NAME TO '$omf/snapcf_$dbname.f';
			SHOW SNAPSHOT CONTROLFILE NAME;
			EOF
		SO
    step_result "RMAN 配置 snapshot controlfile"
  else
    omf=$oradata_dir
    arch=$archive_dir
    step_log "文件系统模式: omf=$omf, arch=$arch"
  fi

  step_log "设置 db_create_file_dest=$omf"
  step_log "设置 log_archive_dest_1=location=$arch"
  execute_sqlplus "$dbname" "" "alter system set db_create_file_dest='$omf';
alter system set log_archive_dest_1='location=$arch';"
  step_result "conf_omf"
}

#==============================================================#
#                    步骤: 配置在线重做日志                        #
#==============================================================#
function conf_redolog() {
  log_print "配置在线重做日志"
  local i thread dbname=$1 redolog_path max_group new_group max_thread is_rac

  step_log "查询数据库 thread 信息..."
  max_thread=$(execute_sqlplus "$dbname" "set pagesize 0" "select max(thread#) from v\$thread;" | tr -d '[:space:]' | grep -xE '[0-9]+' | head -1)
  step_log "数据库最大 thread# = [${max_thread}]"
  if [[ -z "$max_thread" ]]; then
    step_log "警告: 无法获取 thread# 信息，默认按单实例处理"
    max_thread=1
  fi

  # 查询数据库现有 redo 日志大小
  local existing_redo_size
  existing_redo_size=$(execute_sqlplus "$dbname" "set pagesize 0" "select distinct bytes/1024/1024 from v\$log where rownum=1;" | tr -d '[:space:]' | grep -xE '[0-9]+' | head -1)
  step_log "数据库现有 redo 日志大小: [${existing_redo_size}M] (脚本指定: ${redosize}M)"

  if [[ -n "$existing_redo_size" && "$existing_redo_size" -ne "$redosize" ]]; then
    step_log "=========================================="
    step_log "警告: 数据库现有 redo 大小 (${existing_redo_size}M) 与脚本指定值 (${redosize}M) 不一致"
    step_log "跳过添加 redo 日志，请确认后手动处理"
    step_log "=========================================="
    step_log "查询当前 redo 日志状态:"
    execute_sqlplus "$dbname" "col member for a80" "select a.thread#,a.group#,b.member member,a.bytes/1024/1024 \"size(M)\" from v\$log a,v\$logfile b where a.group#=b.group# order by 1,2;"
    return 0
  fi

  step_log "查询各 thread 当前 redo group 数量:"
  execute_sqlplus "$dbname" "col thread# for 999" "select thread#, count(*) as group_count from v\$log group by thread# order by 1;"

  if [[ -n "$max_thread" && "$max_thread" =~ ^[0-9]+$ && "$max_thread" -gt 1 ]]; then
    is_rac=true
    step_log "检测结果: RAC 环境，共 ${max_thread} 个 thread"
  else
    is_rac=false
    step_log "检测结果: 单实例环境"
  fi

  step_log "查询当前最大 group#..."
  max_group=$(execute_sqlplus "$dbname" "set pagesize 0" "select max(group#) from v\$logfile;" | tr -d '[:space:]' | grep -xE '[0-9]+' | head -1)
  step_log "当前最大 group# = [${max_group}]"
  if [[ -z "$max_group" ]]; then
    step_log "错误: 无法获取有效的 group#，跳过 redo 日志配置"
    return 1
  fi

  if $is_rac; then
    for ((i = 0; i < max_thread; i++)); do
      ((thread = i + 1))
      local cur_count
      cur_count=$(execute_sqlplus "$dbname" "set pagesize 0" "select count(*) from v\$log where thread#=$thread;" | tr -d '[:space:]' | grep -xE '[0-9]+' | head -1)
      step_log "thread $thread 当前 redo 组数: ${cur_count}"

      if [[ -n "$cur_count" && "$cur_count" -ge 6 ]]; then
        step_log "thread $thread 已有 ${cur_count} 组 (>=6)，跳过"
        continue
      fi

      local need_add=6
      [[ -n "$cur_count" ]] && need_add=$((6 - cur_count))
      step_log ">>> 处理 thread $thread: 需添加 ${need_add} 组 redo"
      max_group=$((max_group + 5 * i))
      for ((a = 1; a <= need_add; a++)); do
        new_group=$((max_group + a))
        step_log "  添加 group $new_group (thread $thread, size ${redosize}M)..."
        execute_sqlplus "$dbname" "" "alter database add logfile thread $thread group $new_group size ${redosize}M;" || true
      done
      step_result "thread $thread redo 日志添加"
    done
  else
    step_log "单实例模式，查询 redo 路径..."
    redolog_path=$(execute_sqlplus "$dbname" "set pagesize 0" "select substr(member, 1, instr(member, '/', -1, 1)) from v\$logfile where rownum = 1;" | grep -vE '(^$|ORA-|SP2-)' | tail -1 | tr -d '[:space:]')
    step_log "redo 路径: [${redolog_path}]"
    if [[ -z "$redolog_path" ]]; then
      step_log "警告: 无法获取 redo 路径，将使用 OMF 自动管理"
    fi

    local cur_count
    cur_count=$(execute_sqlplus "$dbname" "set pagesize 0" "select count(*) from v\$log;" | tr -d '[:space:]' | grep -xE '[0-9]+' | head -1)
    step_log "当前 redo 总组数: ${cur_count}"

    if [[ -n "$cur_count" && "$cur_count" -ge 6 ]]; then
      step_log "已有 ${cur_count} 组 (>=6)，跳过添加"
    else
      local need_add=6
      [[ -n "$cur_count" ]] && need_add=$((6 - cur_count))
      step_log "需添加 ${need_add} 组 redo"
      for ((a = 1; a <= need_add; a++)); do
        new_group=$((a + max_group))
        if ((new_group < 10)); then
          printf -v new_group "%02d" "$new_group"
        fi
        step_log "  添加 group $new_group (size ${redosize}M)..."
        if [[ "$oracle_install_mode" == "single" ]]; then
          execute_sqlplus "$dbname" "" "alter database add logfile group $new_group '${redolog_path}redo${new_group}.log' size ${redosize}M;" || true
        else
          execute_sqlplus "$dbname" "" "alter database add logfile group $new_group size ${redosize}M;" || true
        fi
      done
      step_result "单实例 redo 日志添加"
    fi
  fi

  step_log "查询最终 redo 日志状态:"
  execute_sqlplus "$dbname" "col member for a80" "select a.thread#,a.group#,b.member member,a.bytes/1024/1024 \"size(M)\" from v\$log a,v\$logfile b where a.group#=b.group# order by 1,2;"
  step_result "conf_redolog"
}

#==============================================================#
#                    步骤: 配置 RMAN 备份脚本                      #
#==============================================================#
function db_backup() {
  log_print "配置 RMAN 备份任务"
  install_package "cron"
  local dbname=$1 scripts_dir=/home/$oracle_user/scripts rman_log_dir="$backup_dir" rman_config

  step_log "脚本目录: $scripts_dir"
  step_log "备份日志目录: $rman_log_dir"
  mkdir -p $scripts_dir
  mkdir -p $rman_log_dir
  step_log "目录创建完成"

  rman_config="allocate channel c1 device type disk;
allocate channel c2 device type disk;
crosscheck backup;
crosscheck archivelog all;
sql\"alter system archive log current\";
delete noprompt expired backup;
delete noprompt obsolete device type disk;"

  local del_arch_script="$scripts_dir/del_arch_$dbname.sh"
  local lv0_backup_script="$scripts_dir/dbbackup_lv0_$dbname.sh"
  local lv1_backup_script="$scripts_dir/dbbackup_lv1_$dbname.sh"

  # 检查同名脚本是否已存在
  if [[ -f "$del_arch_script" && -f "$lv0_backup_script" && -f "$lv1_backup_script" ]]; then
    step_log "数据库 $dbname 的备份脚本已存在，跳过生成"
    step_log "  $del_arch_script"
    step_log "  $lv0_backup_script"
    step_log "  $lv1_backup_script"
    return 0
  fi

  step_log "生成删除归档脚本: $del_arch_script"
  cat >"$del_arch_script" <<DELARCH
#!/bin/bash
source ~/.$dbname
deltime=\$(date +"20%y%m%d%H%M%S")
rman target / nocatalog msglog $scripts_dir/logs/${dbname}/del_arch_\$deltime.log <<-EOF
crosscheck archivelog all;
delete noprompt archivelog until time 'sysdate-7';
delete noprompt force archivelog until time 'SYSDATE-10';
EOF
DELARCH
  chmod +x "$del_arch_script"

  step_log "生成 Level 0 备份脚本: $lv0_backup_script"
  cat >"$lv0_backup_script" <<LV0BACKUP
#!/bin/bash
source ~/.$dbname
backtime=\$(date +"20%y%m%d%H%M%S")
rman target / log=$rman_log_dir/${dbname}/level0_backup_\$backtime.log<<-EOF
run {
$rman_config
backup incremental level 0 database include current controlfile format '$rman_log_dir/${dbname}/backlv0_%T_%t_%s_%p';
backup not backed up 1 times as compressed backupset archivelog all format '$rman_log_dir/${dbname}/arch_%T_%t_%s_%p';
}
EOF
LV0BACKUP
  chmod +x "$lv0_backup_script"

  step_log "生成 Level 1 备份脚本: $lv1_backup_script"
  cat >"$lv1_backup_script" <<LV1BACKUP
#!/bin/bash
source ~/.$dbname
backtime=\$(date +"20%y%m%d%H%M%S")
rman target / log=$rman_log_dir/${dbname}/level1_backup_\$backtime.log<<-EOF
run {
$rman_config
backup incremental level 1 database include current controlfile format '$rman_log_dir/${dbname}/backlv1_%T_%t_%s_%p';
backup not backed up 1 times as compressed backupset archivelog all format '$rman_log_dir/${dbname}/arch_%T_%t_%s_%p';
}
EOF
LV1BACKUP
  chmod +x "$lv1_backup_script"

  mkdir -p "$rman_log_dir/$dbname" "$scripts_dir/logs/$dbname"
  chown -R $oracle_user:oinstall "$rman_log_dir/$dbname" "$scripts_dir/logs/$dbname"

  # crontab: 检查是否已存在该数据库的定时任务，已存在则跳过
  local crontab_file="/var/spool/cron/$oracle_user"
  step_log "配置 crontab: $crontab_file"
  if [[ -f "$crontab_file" ]] && grep -q "del_arch_$dbname.sh" "$crontab_file"; then
    step_log "crontab 中已存在 $dbname 的定时任务，跳过添加"
  else
    # crontab 仅追加，不做还原，避免覆盖其他实例的定时任务
    if [[ ! -f "$crontab_file" ]]; then
      touch "$crontab_file"
      step_log "crontab 文件不存在，已创建"
    fi
    write_file "N" "$crontab_file" "# OracleBegin $dbname
00 02 * * * $del_arch_script
#00 00 * * 0 $lv0_backup_script
#00 00 * * 1,2,3,4,5,6 $lv1_backup_script"
    step_log "已追加 $dbname 定时任务到 crontab"
  fi
  if check_file /etc/cron.allow; then
    write_file "N" "/etc/cron.allow" "$oracle_user"
  fi
  chown -R $oracle_user:oinstall "$scripts_dir" "$rman_log_dir"

  step_log "当前 crontab 内容:"
  cat /var/spool/cron/$oracle_user
  step_log "生成的脚本文件列表:"
  ls -l $scripts_dir/*.sh 2>&1
  step_result "db_backup"
}

#==============================================================#
#                    步骤: 优化数据库参数 ★                        #
#==============================================================#
function conf_para() {
  log_print "优化数据库参数"
  local dbname=$1 nums=$2

  # 获取物理内存
  step_log "查询物理内存..."
  os_memory_total=$(awk '/^MemTotal:/ { print $2; }' /proc/meminfo)
  local mem_gb=$((os_memory_total / 1024 / 1024))
  step_log "物理内存: ${os_memory_total} KB (${mem_gb} GB)"

  # SGA/PGA 优先级: -S/-G 手动指定 > -M 总内存自动分配 > 按物理内存自动计算
  local calc_sga calc_pga

  if [[ -n "$sga_target" || -n "$pga_target" ]]; then
    # 优先级1: -S/-G 手动指定（未指定的仍自动计算）
    if [[ -n "$sga_target" ]]; then
      calc_sga="$sga_target"
      step_log "SGA_TARGET: 手动指定 = $calc_sga"
    else
      ((calc_sga = (os_memory_total * 8 * 8 / 100 / 1024 / nums)))
      calc_sga="${calc_sga}M"
      step_log "SGA_TARGET: 自动计算 (内存64%/实例数) = $calc_sga"
    fi
    if [[ -n "$pga_target" ]]; then
      calc_pga="$pga_target"
      step_log "PGA_AGGREGATE_TARGET: 手动指定 = $calc_pga"
    else
      ((calc_pga = (os_memory_total * 8 * 2 / 100 / 1024 / nums)))
      calc_pga="${calc_pga}M"
      step_log "PGA_AGGREGATE_TARGET: 自动计算 (内存16%/实例数) = $calc_pga"
    fi
  elif [[ -n "$db_memory" ]]; then
    # 优先级2: -M 指定总内存，按 SGA:PGA = 80:20 分配
    local upper=${db_memory^^}
    local num=${upper%M}
    num=${num%G}
    local db_mem_mb
    case "$upper" in
      *G) db_mem_mb=$((num * 1024)) ;;
      *M) db_mem_mb=$num ;;
      *)  db_mem_mb=$num ;;
    esac
    calc_sga="$((db_mem_mb * 80 / 100))M"
    calc_pga="$((db_mem_mb * 20 / 100))M"
    step_log "按 -M 指定总内存 $db_memory (${db_mem_mb}MB) 分配: SGA=80%=$calc_sga, PGA=20%=$calc_pga"
  else
    # 优先级3: 按物理内存自动计算
    ((calc_sga = (os_memory_total * 8 * 8 / 100 / 1024 / nums)))
    calc_sga="${calc_sga}M"
    ((calc_pga = (os_memory_total * 8 * 2 / 100 / 1024 / nums)))
    calc_pga="${calc_pga}M"
    step_log "按物理内存自动计算: nums=$nums, SGA_TARGET=$calc_sga, PGA_AGGREGATE_TARGET=$calc_pga"
  fi
  sga_target="$calc_sga"
  pga_target="$calc_pga"
  step_log "最终生效: SGA_TARGET=$sga_target, PGA_AGGREGATE_TARGET=$pga_target"

  # ---- 1. RAC 专属优化 ----
  if [[ "$oracle_install_mode" == "rac" ]]; then
    step_log ">>> [1/6] 配置 RAC 专属参数..."
    execute_sqlplus "$dbname" "" "alter system set parallel_force_local=true sid='*' scope=spfile;
alter system set \"_gc_policy_time\"=0 scope=spfile;
alter system set \"_gc_undo_affinity\"=false scope=spfile;
alter system set \"_clusterwide_global_transactions\"=FALSE scope=spfile;" || true
    step_result "RAC 专属参数"
  else
    step_log ">>> [1/6] 非 RAC 环境，跳过 RAC 专属参数"
  fi

  # ---- 2. 禁用 ORACLE_OCM ----
  step_log ">>> [2/6] 禁用 ORACLE_OCM 调度任务..."
  execute_sqlplus "$dbname" "" "exec dbms_scheduler.disable('ORACLE_OCM.MGMT_CONFIG_JOB');
exec dbms_scheduler.disable('ORACLE_OCM.MGMT_STATS_CONFIG_JOB');" || true
  step_result "禁用 ORACLE_OCM"

  # ---- 3. 禁用自动维护 Advisor ----
  step_log ">>> [3/6] 禁用自动维护 Advisor..."
  execute_sqlplus "$dbname" "" "BEGIN
DBMS_AUTO_TASK_ADMIN.DISABLE(
client_name => 'auto space advisor',
operation => NULL,
window_name => NULL);
END;
/
BEGIN
DBMS_AUTO_TASK_ADMIN.DISABLE(
client_name => 'sql tuning advisor',
operation => NULL,
window_name => NULL);
END;
/" || true
  step_result "禁用自动维护 Advisor"

  # ---- 4. 密码策略 ----
  step_log ">>> [4/6] 配置密码策略（取消所有限制）..."
  execute_sqlplus "$dbname" "" "alter profile default limit password_grace_time unlimited;
alter profile default limit password_life_time unlimited;
alter profile default limit password_lock_time unlimited;
alter profile default limit failed_login_attempts unlimited;" || true
  step_result "密码策略"

  # ---- 5. 通用优化参数（使用传参变量） ----
  step_log ">>> [5/6] 配置通用数据库优化参数..."
  step_log "  audit_trail=none"
  step_log "  processes=$processes, open_cursors=$open_cursors"
  step_log "  session_cached_cursors=$session_cached_cursors, db_files=$db_files"
  step_log "  sga_max_size=$sga_target, sga_target=$sga_target, pga_aggregate_target=$pga_target"
  step_log "  _undo_autotune=false, undo_retention=$undo_retention"
  step_log "  control_file_record_keep_time=31"
  step_log "  event=28401,10949"
  step_log "  _b_tree_bitmap_plans=false, deferred_segment_creation=false"
  step_log "  _optimizer_adaptive_cursor_sharing=false"
  step_log "  _optimizer_extended_cursor_sharing=none"
  step_log "  _optimizer_extended_cursor_sharing_rel=none"
  step_log "  _optimizer_use_feedback=false"
  step_log "  _cleanup_rollback_entries=2000"
  step_log "  _datafile_write_errors_crash_instance=false"
  step_log "  parallel_max_servers=$parallel_max_servers"
  step_log "  清除 AMM 自动内存管理参数（不存在则跳过）"
  execute_sqlplus "$dbname" "" "DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count FROM v\$spparameter WHERE name='memory_target' AND value IS NOT NULL;
  IF v_count > 0 THEN EXECUTE IMMEDIATE 'alter system reset memory_target sid=''*'' scope=spfile'; END IF;
  SELECT COUNT(*) INTO v_count FROM v\$spparameter WHERE name='memory_max_target' AND value IS NOT NULL;
  IF v_count > 0 THEN EXECUTE IMMEDIATE 'alter system reset memory_max_target sid=''*'' scope=spfile'; END IF;
  SELECT COUNT(*) INTO v_count FROM v\$spparameter WHERE name='db_recovery_file_dest' AND value IS NOT NULL;
  IF v_count > 0 THEN EXECUTE IMMEDIATE 'alter system reset db_recovery_file_dest'; END IF;
  SELECT COUNT(*) INTO v_count FROM v\$spparameter WHERE name='db_recovery_file_dest_size' AND value IS NOT NULL;
  IF v_count > 0 THEN EXECUTE IMMEDIATE 'alter system reset db_recovery_file_dest_size'; END IF;
END;
/"
  step_result "清除 AMM/FRA 参数"

  execute_sqlplus "$dbname" "" "alter system set audit_trail=none sid='*' scope=spfile;
alter system set sga_max_size=$sga_target sid='*' scope=spfile;
alter system set sga_target=$sga_target sid='*' scope=spfile;
alter system set pga_aggregate_target=$pga_target sid='*' scope=spfile;
alter system set processes=$processes scope=spfile;
alter system set open_cursors=$open_cursors scope=spfile;
alter system set session_cached_cursors=$session_cached_cursors scope=spfile;
alter system set db_files=$db_files scope=spfile;
alter system set \"_undo_autotune\"=false sid='*' scope=spfile;
alter system set undo_retention=$undo_retention scope=spfile;
alter system set control_file_record_keep_time=31;
alter system set event='28401 trace name context forever,level 1','10949 trace name context forever,level 1' sid='*' scope=spfile;
alter system set \"_b_tree_bitmap_plans\"=false sid='*';
alter system set deferred_segment_creation=false sid='*';
alter system set \"_optimizer_adaptive_cursor_sharing\"=false sid='*' scope=spfile;
alter system set \"_optimizer_extended_cursor_sharing\"=none sid='*' scope=spfile;
alter system set \"_optimizer_extended_cursor_sharing_rel\"=none sid='*' scope=spfile;
alter system set \"_optimizer_use_feedback\"=false sid ='*' scope=spfile;
alter system set \"_cleanup_rollback_entries\"=2000 sid='*' scope=spfile;
alter system set \"_datafile_write_errors_crash_instance\"=false sid='*';
alter system set parallel_max_servers=$parallel_max_servers sid='*';" || true
  step_result "通用数据库优化参数"

  # ---- 6. 从 spfile 生成 pfile 验证参数 ----
  step_log ">>> [6/6] 从 spfile 生成 pfile 并校验参数..."
  local pfile="/tmp/init${dbname}.ora"
  execute_sqlplus "$dbname" "" "create pfile='$pfile' from spfile;"
  if [[ -f "$pfile" ]]; then
    step_log "pfile 已生成: $pfile"
    chown $oracle_user:oinstall "$pfile"

    step_log "========== 参数校验结果 =========="
    local check_pass=true fail_count=0

    check_param() {
      local name=$1 expect=$2 actual
      actual=$(grep -iE "^(\*\.)?${name}\s*=" "$pfile" | head -1 | sed 's/.*=\s*//' | tr -d "'" | tr -d '"')
      local expect_lower=${expect,,} actual_lower=${actual,,}
      # 期望值带单位(M/G/K)时，将 pfile 中的字节值转换为同单位做数值比较
      if [[ "$expect" =~ [MGK]$ && "$actual" =~ ^[0-9]+$ ]]; then
        local actual_num expect_num unit=${expect^^}
        case "$unit" in
          *G) actual_num=$((actual / 1024 / 1024 / 1024)); expect_num=${expect%G} ;;
          *M) actual_num=$((actual / 1024 / 1024));         expect_num=${expect%M} ;;
          *K) actual_num=$((actual / 1024));                 expect_num=${expect%K} ;;
        esac
        if ((actual_num == expect_num)); then
          step_log "  [OK] $name = ${actual_num}${unit: -1}"
        else
          step_log "  [FAIL] $name = ${actual_num}${unit: -1} (期望: $expect)"
          check_pass=false; ((fail_count++))
        fi
      elif [[ "$actual_lower" == *"$expect_lower"* ]]; then
        step_log "  [OK] $name = $actual"
      else
        step_log "  [FAIL] $name = $actual (期望: $expect)"
        check_pass=false; ((fail_count++))
      fi
    }

    # ---- 通用参数 ----
    check_param "processes" "$processes"
    check_param "open_cursors" "$open_cursors"
    check_param "session_cached_cursors" "$session_cached_cursors"
    check_param "db_files" "$db_files"
    check_param "undo_retention" "$undo_retention"
    check_param "parallel_max_servers" "$parallel_max_servers"
    check_param "sga_max_size" "$sga_target"
    check_param "sga_target" "$sga_target"
    check_param "pga_aggregate_target" "$pga_target"
    check_param "control_file_record_keep_time" "31"
    check_param "audit_trail" "none"
    check_param "deferred_segment_creation" "false"
    check_param "_undo_autotune" "false"
    check_param "_b_tree_bitmap_plans" "false"
    check_param "_optimizer_adaptive_cursor_sharing" "false"
    check_param "_optimizer_extended_cursor_sharing" "none"
    check_param "_optimizer_extended_cursor_sharing_rel" "none"
    check_param "_optimizer_use_feedback" "false"
    check_param "_cleanup_rollback_entries" "2000"
    check_param "_datafile_write_errors_crash_instance" "false"

    # ---- RAC 专属参数 ----
    if [[ "$oracle_install_mode" == "rac" ]]; then
      check_param "parallel_force_local" "true"
      check_param "_gc_policy_time" "0"
      check_param "_gc_undo_affinity" "false"
      check_param "_clusterwide_global_transactions" "false"
    fi

    # ---- 存储与归档 ----
    check_param "db_create_file_dest" "+$data_asm_group"
    check_param "log_archive_dest_1" "location=+$arch_asm_group"

    step_log "==================================="
    local total_check=13
    [[ "$oracle_install_mode" == "rac" ]] && total_check=$((total_check + 9))
    if $check_pass; then
      step_log "校验结果: 全部通过 (${total_check} 项)"
    else
      step_log "校验结果: ${fail_count} 项未匹配（已写入 spfile，重启后将生效）"
    fi
  else
    step_log "警告: pfile 生成失败，跳过参数校验"
  fi
  step_result "conf_para 完成"
}

#==============================================================#
#                    步骤: 配置 SQLNET.ORA                       #
#==============================================================#
function conf_sqlnet() {
  log_print "配置 sqlnet.ora"
  local sqlnet_file="$env_oracle_home/network/admin/sqlnet.ora"

  step_log "sqlnet.ora 路径: $sqlnet_file"
  local sqlnet_dir
  sqlnet_dir=$(dirname "$sqlnet_file")
  if [[ ! -d "$sqlnet_dir" ]]; then
    step_log "目录 $sqlnet_dir 不存在，创建中..."
    mkdir -p "$sqlnet_dir"
    chown "$oracle_user:oinstall" "$sqlnet_dir"
    step_result "创建目录 $sqlnet_dir"
  fi

  if check_file "$sqlnet_file"; then
    step_log "sqlnet.ora 已存在，先备份"
    backup_restore_file "$sqlnet_file"
  else
    step_log "sqlnet.ora 不存在，将新建"
    touch "$sqlnet_file"
    chown "$oracle_user:oinstall" "$sqlnet_file"
  fi

  step_log "追加 SQLNET 配置: ALLOWED_LOGON_VERSION_CLIENT=8, SERVER=8"
  {
    echo "# OracleBegin"
    echo "SQLNET.ALLOWED_LOGON_VERSION_CLIENT=8"
    echo "SQLNET.ALLOWED_LOGON_VERSION_SERVER=8"
  } >> "$sqlnet_file"
  step_result "写入 sqlnet.ora"

  step_log "验证 sqlnet.ora 内容:"
  cat "$sqlnet_file"

  if [[ "$oracle_install_mode" == "rac" && ${#rac_public_ips[@]} -gt 1 ]]; then
    step_log "RAC 模式：分发 sqlnet.ora 到其他节点"
    for ip in "${rac_public_ips[@]:1}"; do
      step_log "scp -> $ip"
      scp -q "$sqlnet_file" "$ip:$sqlnet_file" 2>&1
      step_result "scp sqlnet.ora to $ip"
    done
  fi

  step_result "conf_sqlnet"
}

#==============================================================#
#                    步骤: 配置 glogin.sql                       #
#==============================================================#
function conf_glogin() {
  log_print "配置 glogin.sql"

  write_glogin_sql_config() {
    local target_file="$1"
    step_log "写入 glogin.sql: $target_file"
    write_file "Y" "$target_file" "define _editor=vi
set serveroutput on size 1000000
set trimspool on
set long 5000
set linesize 100
set pagesize 9999
column plan_plus_exp format a80
set sqlprompt '&_user.@&_connect_identifier. SQL> '"
  }

  step_log "备份并写入 Oracle 用户的 glogin.sql..."
  backup_restore_file "$env_oracle_home/sqlplus/admin/glogin.sql"
  write_glogin_sql_config "$env_oracle_home/sqlplus/admin/glogin.sql"

  if [[ "$oracle_install_mode" == "rac" && ${#rac_public_ips[@]} -gt 1 ]]; then
    step_log "备份并写入 Grid 用户的 glogin.sql..."
    backup_restore_file "$env_grid_home/sqlplus/admin/glogin.sql"
    write_glogin_sql_config "$env_grid_home/sqlplus/admin/glogin.sql"
    for ip in "${rac_public_ips[@]:1}"; do
      step_log "分发 glogin.sql 到 $ip..."
      run_as_oracle "scp -q $env_oracle_home/sqlplus/admin/glogin.sql $ip:$env_oracle_home/sqlplus/admin/"
      step_result "分发 glogin.sql to $ip"
    done
  fi

  step_log "glogin.sql 最终内容:"
  grep -v "^\s*\(#\|$\|--\)" "$env_oracle_home/sqlplus/admin/glogin.sql"
  step_result "conf_glogin"
}

#==============================================================#
#                    步骤: 重启数据库                              #
#==============================================================#
function db_restart() {
  local dbname=$1
  log_print "重启数据库: $dbname"

  if [[ "$oracle_install_mode" == "rac" ]]; then
    step_log "RAC 环境，使用 srvctl 重启数据库 $dbname"
    step_log ">>> [1/3] 停止数据库..."
    su - $oracle_user -c "export ORACLE_SID=$dbname; srvctl stop database -d $dbname" 2>&1
    step_result "srvctl stop database $dbname"
    step_log "等待 10 秒..."
    sleep 10
    step_log ">>> [2/3] 启动数据库..."
    su - $oracle_user -c "export ORACLE_SID=$dbname; srvctl start database -d $dbname" 2>&1
    step_result "srvctl start database $dbname"
    step_log ">>> [3/3] 检查数据库状态..."
    sleep 5
    su - $oracle_user -c "export ORACLE_SID=$dbname; srvctl status database -d $dbname" 2>&1
  else
    step_log "单实例环境，使用 sqlplus 重启数据库 $dbname"
    step_log ">>> [1/3] 关闭数据库 (shutdown immediate)..."
    su - $oracle_user -c "export ORACLE_SID=$dbname; sqlplus -S / as sysdba<<'EOF'
shutdown immediate;
EOF
" 2>&1
    step_result "shutdown immediate"
    step_log "等待 10 秒..."
    sleep 10
    step_log ">>> [2/3] 启动数据库 (startup)..."
    su - $oracle_user -c "export ORACLE_SID=$dbname; sqlplus -S / as sysdba<<'EOF'
startup;
EOF
" 2>&1
    step_result "startup"
    step_log ">>> [3/3] 检查数据库实例状态..."
    sleep 5
    su - $oracle_user -c "export ORACLE_SID=$dbname; sqlplus -S / as sysdba<<'EOF'
select instance_name, status, database_status from v\;
exit;
EOF
" 2>&1
  fi
  step_result "重启数据库 $dbname"
}


#==============================================================#
#                     总执行入口                                #
#==============================================================#
function db_optimize() {
  for name in "${db_names[@]}"; do
    step_log "==================== 开始优化数据库: $name ===================="

    if should_run "omf"; then
      conf_omf "$name"
    else
      step_log "跳过: conf_omf"
    fi

    if should_run "redolog"; then
      conf_redolog "$name"
    else
      step_log "跳过: conf_redolog"
    fi

    if should_run "backup"; then
      db_backup "$name"
    else
      step_log "跳过: db_backup"
    fi

    if should_run "para"; then
      conf_para "$name" ${#db_names[@]}
    else
      step_log "跳过: conf_para"
    fi

    step_log "==================== 数据库 $name 优化完成 ===================="
  done

  if should_run "glogin"; then
    conf_glogin
  else
    step_log "跳过: conf_glogin"
  fi
}

#==============================================================#
#                          主流程                                #
#==============================================================#

# 校验 root 权限
if [ "$(id -u)" -ne 0 ]; then
  echo "请以 root 用户执行此脚本！"
  exit 1
fi

# 支持多实例，逗号分隔
IFS=',' read -ra db_names <<<"$db_name"

echo
color_printf blue "=========================================="
color_printf blue "  Oracle 19c 数据库参数优化"
color_printf blue "  日志文件 : $oracleinstalllog"
color_printf blue "  数据库名称: $db_name"
color_printf blue "  安装模式 : $oracle_install_mode"
color_printf blue "  Oracle Home: $env_oracle_home"
color_printf blue "  Grid Home  : $env_grid_home"
color_printf blue "  Oracle 用户: $oracle_user"
color_printf blue "  执行时间  : $(date '+%Y-%m-%d %H:%M:%S')"
print_enabled_steps
color_printf blue "=========================================="

# 执行优化
db_optimize

# sqlnet 作为独立步骤（不包含在 db_optimize 循环内）
if should_run "sqlnet"; then
  conf_sqlnet
else
  step_log "跳过: conf_sqlnet"
fi


	# 重启数据库（-z 参数启用，执行前需用户确认）
	if $restart_after; then
	  for name in "${db_names[@]}"; do
	    echo
	    color_printf yellow "====== 即将重启数据库: $name ======"

	    color_printf yellow "  模式: $oracle_install_mode"
	    echo -n "  确认重启数据库 $name 吗？(yes/no): "
	    read -r confirm
	    if [[ "$confirm" == "yes" || "$confirm" == "YES" || "$confirm" == "y" ]]; then
	      db_restart "$name"
	    else
	      step_log "用户取消，跳过重启数据库 $name"
	    fi
	  done
	fi

echo
color_printf green "====== Oracle 19c 数据库参数优化全部完成 ======"
step_log "全部完成，日志文件: $oracleinstalllog"
echo
