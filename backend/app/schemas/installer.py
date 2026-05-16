from pydantic import BaseModel
from typing import Literal


# ASM-only fields (standalone + rac)
ASM_FIELDS = frozenset([
    "grid_user", "grid_passwd", "asm_disk_conf", "multipath",
    "data_base_disk", "data_asm_group", "data_redun", "grid_patch",
    "virtualbox",
])

# RAC-only fields
RAC_FIELDS = frozenset([
    "rac_priv_ifname", "rac_hostname", "rac_public_ip", "rac_virtual_ip",
    "rac_scan_ip", "root_passwd", "cluster_name", "scan_name",
    "ocr_base_disk", "arch_base_disk", "ocr_asm_group", "arch_asm_group",
    "ocr_redun", "arch_redun", "timeserver_ip",
    "dns", "dns_name", "dns_ip", "install_until_grid",
])

# [field_name, flag, default_value]
FLAG_MAP = [
    # common
    ("mode", "-install_mode", ""),
    ("gi_version", "-giv", ""),
    ("db_version", "-dbv", ""),
    ("local_repo", "-lrp", "Y"),
    ("net_repo", "-nrp", "N"),
    ("local_ifname", "-lf", ""),
    ("hostname", "-n", "orcl"),
    ("oracle_user", "-ou", "oracle"),
    ("oracle_passwd", "-op", "oracle"),
    ("database_passwd", "-dp", "oracle"),
    ("env_base_dir", "-d", "/u01"),
    ("oradata_dir", "-ord", "/oradata"),
    ("db_name", "-o", "orcl"),
    ("db_characterset", "-ds", "AL32UTF8"),
    ("nation_characterset", "-ns", "AL16UTF16"),
    ("db_block_size", "-dbs", 8192),
    ("enable_arch", "-er", "true"),
    ("pdbname", "-pdb", "pdb01"),
    ("redosize", "-redo", 1024),
    ("isgui", "-gui", "N"),
    ("huge_flag", "-hf", "N"),
    ("only_conf_os", "-m", "N"),
    ("install_until_db", "-ud", "N"),
    ("optimize_db", "-opd", "N"),
    ("oracle_patch", "-opa", ""),
    ("ojvm_patch", "-jpa", ""),
    # ASM
    ("archive_dir", "-ard", "/oradata/archivelog"),
    ("grid_user", "-gu", "grid"),
    ("grid_passwd", "-gp", "oracle"),
    ("asm_disk_conf", "-adc", "Y"),
    ("multipath", "-mp", "Y"),
    ("data_base_disk", "-dd", ""),
    ("data_asm_group", "-dn", "DATA"),
    ("data_redun", "-dr", "EXTERNAL"),
    ("grid_patch", "-gpa", ""),
    ("virtualbox", "-vbox", "N"),
    # RAC
    ("rac_priv_ifname", "-pf", ""),
    ("rac_hostname", "-hn", ""),
    ("rac_public_ip", "-ri", ""),
    ("rac_virtual_ip", "-vi", ""),
    ("rac_scan_ip", "-si", ""),
    ("root_passwd", "-rp", ""),
    ("cluster_name", "-cn", ""),
    ("scan_name", "-sn", ""),
    ("ocr_base_disk", "-od", ""),
    ("arch_base_disk", "-ad", ""),
    ("ocr_asm_group", "-on", "OCR"),
    ("arch_asm_group", "-an", "ARCH"),
    ("ocr_redun", "-or", "EXTERNAL"),
    ("arch_redun", "-ar", "EXTERNAL"),
    ("timeserver_ip", "-tsi", ""),
    ("dns", "-dns", "N"),
    ("dns_name", "-dnsn", ""),
    ("dns_ip", "-dnsi", ""),
    ("install_until_grid", "-ug", "N"),
]


class InstallRequest(BaseModel):
    mode: Literal["single", "standalone", "rac"] = "single"
    gi_version: str = ""
    db_version: str = ""
    local_repo: str = "Y"
    net_repo: str = "N"
    local_ifname: str = ""
    hostname: str = "orcl"
    oracle_user: str = "oracle"
    oracle_passwd: str = "oracle"
    database_passwd: str = "oracle"
    env_base_dir: str = "/u01"
    oradata_dir: str = "/oradata"
    db_name: str = "orcl"
    db_characterset: str = "AL32UTF8"
    nation_characterset: str = "AL16UTF16"
    db_block_size: int = 8192
    enable_arch: str = "true"
    pdbname: str = "pdb01"
    redosize: int = 1024
    isgui: str = "N"
    huge_flag: str = "N"
    only_conf_os: str = "N"
    install_until_db: str = "N"
    optimize_db: str = "N"
    oracle_patch: str = ""
    ojvm_patch: str = ""
    archive_dir: str = "/oradata/archivelog"
    grid_user: str = "grid"
    grid_passwd: str = "oracle"
    asm_disk_conf: str = "Y"
    multipath: str = "Y"
    data_base_disk: str = ""
    data_asm_group: str = "DATA"
    data_redun: str = "EXTERNAL"
    grid_patch: str = ""
    virtualbox: str = "N"
    rac_priv_ifname: str = ""
    rac_hostname: str = ""
    rac_public_ip: str = ""
    rac_virtual_ip: str = ""
    rac_scan_ip: str = ""
    root_passwd: str = ""
    cluster_name: str = ""
    scan_name: str = ""
    ocr_base_disk: str = ""
    arch_base_disk: str = ""
    ocr_asm_group: str = "OCR"
    arch_asm_group: str = "ARCH"
    ocr_redun: str = "EXTERNAL"
    arch_redun: str = "EXTERNAL"
    timeserver_ip: str = ""
    dns: str = "N"
    dns_name: str = ""
    dns_ip: str = ""
    install_until_grid: str = "N"


class InstallResponse(BaseModel):
    command: str
    params_summary: list[str]
