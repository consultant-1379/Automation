# awk returns list of  PDBs with ALLOWED DISRUPTION value set to zero
awk_cmd = "$2 == 0 {print $1}"
