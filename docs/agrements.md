## Auth
Login for every kind of users have two step verification
1. User Send "Login <username> <password>"
2. Server send back "LoginSuc <token> <rule>"
   1. if not success send back "LoginFail UserNotFound" or "LoginFail UserNotApprove"

Signup for every kind of users have two step verification
1. User Send "Singup <username> <password> <access_level>"
   1. access_level : normal user=1 admin=2
      1. manager is not registable and we have only one default manager
2. Server send back "SingupSuc"
   1. if not success send back "SignUpFail"
Note:After Signup you should login

Logout for every kind of users have two step verification
1. User Send "Logout <token>"
2. Server send back "LogoutSuc"
ps:After logging out we stay in menu



## Video
1. user send "UploadVideo <token> <file_name>"
2. server send "Upload" or "UploadFail"
3. user send video
4. user send VideoFinished
5. server saves file under videos directory

## Reacts
1. user send react
2. server send "ReactSuc" or "ReactFail"

## Ban
1. user send ban req
2. server send "BanSuc" or "BanFail"

## Aprove admin account
1. manager send "App <token> <username>"
2. server send "AppSuc" or "AppFail"


## Tickets
### New Ticket
1. user send "NewTicket <token> <text>"
2. server send "NewTicketSuc" or "NewTicketFail"

### Answer Ticket
1. admin send "AnswerTicket <token> <ticket_id> <comment>"
2. server send "AnswerTicketSuc" or "AnswerTicketFail"

## change ticket state
1. admin send "ChangeTicketState <token> <ticket_id> <new_state>"
2. server send "ChangeTicketStateSuc" or "ChangeTicketStateFail"

## See tickets
1. user send "GetTickets <token>"
2. server send "GetTicketsSuc <list_of_tickets>" or "GetTicketsFail"