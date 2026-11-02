from django.shortcuts import render
import secrets
import string


def home(request):
    password = ""
    error = ""

    if request.method == "POST":

        # Get password length
        try:
            length = int(request.POST.get("length", 12))
        except (ValueError, TypeError):
            length = 12


        # Minimum password length validation
        if length < 8:
            error = "Password length must be at least 8 characters."

        else:

            # Check whether ambiguous characters should be excluded
            exclude_ambiguous = request.POST.get(
                "exclude_ambiguous"
            )

            # Character groups
            uppercase = string.ascii_uppercase
            lowercase = string.ascii_lowercase
            numbers = string.digits
            symbols = string.punctuation


            # Remove ambiguous characters
            if exclude_ambiguous:

                uppercase = uppercase.replace("O", "")

                lowercase = lowercase.replace("l", "")

                numbers = numbers.replace("0", "").replace("1", "")


            # Store selected character groups
            selected_groups = []


            if request.POST.get("uppercase"):
                selected_groups.append(uppercase)


            if request.POST.get("lowercase"):
                selected_groups.append(lowercase)


            if request.POST.get("numbers"):
                selected_groups.append(numbers)


            if request.POST.get("symbols"):
                selected_groups.append(symbols)


            # Require at least 2 character types
            if len(selected_groups) < 2:

                error = (
                    "Please select at least 2 character types."
                )


            else:

                # Add at least one character from every selected group
                password_characters = [

                    secrets.choice(group)

                    for group in selected_groups
                ]


                # Combine all selected groups
                all_characters = "".join(selected_groups)


                # Fill remaining password length
                for _ in range(
                    length - len(password_characters)
                ):

                    password_characters.append(
                        secrets.choice(all_characters)
                    )


                # Securely shuffle password
                secrets.SystemRandom().shuffle(
                    password_characters
                )


                # Create final password
                password = "".join(password_characters)


    return render(
        request,
        "index.html",
        {
            "password": password,
            "error": error,
        }
    )