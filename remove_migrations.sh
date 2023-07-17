rm -r ./media/*
printf "Deleted Media Files!"

rm -r ./apps/authentication/migrations/*
rm -r ./apps/croud_founding/migrations/*
rm -r ./apps/users_management/migrations/*


printf "Migrations files removed successfully!"

printf "\n"

touch ./apps/users_management/migrations/__init__.py
touch ./apps/croud_founding/migrations/__init__.py

printf "Migrations __init__ created successfully!"
