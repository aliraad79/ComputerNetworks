## Auth
Login for every kind of users have two step verification
1. User Send "Login <username> <password>"
2. Server send back "LoginSuc <token>"
   1. if not success send back "LoginFail"

Signup for every kind of users have two step verification
1. User Send "Singup <username> <password> <type>"
   1. type : normal user=1 admin=2 manager=3
2. Server send back "SingupSuc <token>"
   1. if not success send back "SignUpFail"

Logout for every kind of users have two step verification
1. User Send "Logout <username>"
2. Server send back "LogoutSuc"
ps:After logging out we stay in menu



## File
1. user send UploadFile
2. user send file
3. user send FileFinished

## Reacts
1. user send react
2. server send "ReactSuc" or "ReactFail"

## Ban
1. user send ban req
2. server send "BanSuc" or "BanFail"