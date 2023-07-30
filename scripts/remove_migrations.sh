# rm -r ./media/*
# printf "Deleted Media Files!"

rm -r ./apps/authentication/migrations/*
# rm -r ./apps/core_study_care/migrations/*
rm -r ./apps/notification_manager/migrations/*
rm -r ./apps/users_management/migrations/*


printf "Migrations files removed successfully!"

printf "\n"

touch ./apps/authentication/migrations/__init__.py
# touch ./apps/core_study_care/migrations/__init__.py
touch ./apps/notification_manager/migrations/__init__.py
touch ./apps/users_management/migrations/__init__.py


printf "Migrations __init__ created successfully!"
