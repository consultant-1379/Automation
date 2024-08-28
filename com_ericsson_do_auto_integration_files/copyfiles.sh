function run_with_password {
    cmd="$2"
    paswd="$1"
    expect << END
        set timeout 60
        spawn $cmd
        expect {
            "*assword*" { send -- $paswd\r }
        }
        expect EOF
        catch wait result
        exit [lindex \$result 3]
END
}
#Here $1 is password and $2 is command
run_with_password $1 "$2"
echo $?
