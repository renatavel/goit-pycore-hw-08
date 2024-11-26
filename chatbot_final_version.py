from collections import UserDict
from datetime import datetime
import pickle 

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if self.is_valid(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must be exactly 10 digits.")

    
    def is_valid(self, phone):
        return len(phone) == 10 and phone.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY.")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None


    def add_phone(self, phone):
        if phone not in [p.value for p in self.phones]:
            self.phones.append(Phone(phone))
        else:
            print("This phone number is already in the list.")

   
    def remove_phone(self, phone):
        phone_to_remove = next((p for p in self.phones if p.value == phone), None)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            print("Phone number not found.")


    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = next((p for p in self.phones if p.value == old_phone), None)
        if not phone_to_edit:
            raise ValueError("Old phone number does not exist.")
        
        if not Phone(new_phone).is_valid(new_phone):
            raise ValueError("New phone number is invalid. It must be 10 digits.")
        
        phone_to_edit.value = new_phone

   
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = ', '.join(p.value for p in self.phones)
        birthday = self.birthday.value if self.birthday else "N/A"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {birthday}"


class AddressBook(UserDict):
    
    def add_record(self, record):
        if record.name.value not in self.data:
            self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

 
    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"No contact found with name {name}.")

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.today()
        for record in self.data.values():
            if record.birthday:
                birthday = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                if birthday.month == today.month and birthday.day >= today.day:
                    upcoming.append(record)
        return upcoming

    def __str__(self):
        return "\n".join(f"{name}: {record}" for name, record in self.data.items())


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IndexError:
            return "Please provide the correct number of arguments: name and phone."
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
    return wrapper


@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    return cmd.strip().lower(), args


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_phone(phone)
    return "Contact added."


@input_error
def change_contact(args, book):
    name, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(record.phones[0].value, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    user_name = args[0]
    record = book.find(user_name)
    if record:
        return record.phones[0].value
    return "Phone number not found."

@input_error
def show_all(book):
    if not book:
        return "No contacts found."
    return "\n".join(f"{name}: {record}" for name, record in book.items())


def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    user_name = args[0]
    record = book.find(user_name)
    if record and record.birthday:
        return f"{user_name}'s birthday: {record.birthday.value}"
    return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{record.name.value}: {record.birthday.value}" for record in upcoming)

@input_error
def main():
    book=load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Goodbye!")
            save_data(book)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()