from collections import UserDict
from datetime import datetime
import re
import pickle
from pathlib import Path


ENDINGS = ['good bye!', 'close', 'exit', '.'] 

def end():
    print('Good bye!')



def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            print('Nie znaleziono podanego kontaktu, wprowadź kontakt poprawnie lub dodaj nowy')
            return
        except ValueError:
            print('Telefon musi składać się z samych cyfr')
            return
        except IndexError:
            print('Nie istnieje kontakt o podanym indeksie')
            return
    return wrapper



class AddressBook(UserDict):
    
    @input_error
    def search(self, arg):
        print(f' Numer(y) do {arg.name.value}: {self.data[arg.name.value][0]}, urodziny {self.data[arg.name.value][1]}')

    def find(self, arg):
        result = {}
        for k, v in self.data.items():
            # print(k,v,arg)
            if arg in k or arg in v[0]:
                result.update({k: v})
        print(result)
    @input_error
    def add_record(self, arg):
        if arg.name.value in self.data and arg.birthday == None:
            self.data[arg.name.value][0].append(arg.phone.value)
        elif arg.name.value not in self.data and arg.birthday != None:
            self.data[arg.name.value] = [[arg.phone.value], arg.birthday.value]
        else:
            self.data[arg.name.value] = [[arg.phone.value], arg.birthday]
    
        print(self.data)

    def iterator(self, n):
        keys = list(self.data.keys())
        index = 0
        while index < len(keys):
            yield {k: self.data[k] for k in keys[index:index+int(n)]}
            index += int(n)
    
    def save_to_file(self, name):
        with open(name, 'wb') as fh:
            pickle.dump(self, fh)

    def read_from_file(self, path):
        with open(path, 'rb') as fh:
            return pickle.load(fh)

class Field:
    def __init__(self, value=None):
        self.value = value


class Name(Field):
    def __init__(self, value):
        super().__init__(value)
    

class Birthday(Field):
    def __init__(self, value):
        self.value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, bday):
        check = re.findall(r'\d{2}[.]\d{2}[.]\d{4}', bday.value)
        if len(check) == 0:
            print('Date należy podać w formacie dd.mm.rrrr')
        else:
            self._value = bday



class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, phone):
        print(phone.value)
        if phone.value.isdigit():
            self._value = phone
        else:
            raise ValueError('numer telefonu musi składać się z samych cyfr')


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name.value
        if phone != None:
            self.phone = phone.value
        else:
            self.phone = []
        if birthday == None:
            self.birthday = birthday
        else:
            self.birthday = birthday.value

    def days_to_birthday(self, arg, today, contacts_c):
        diff = today - datetime.strptime(contacts_c[arg.name.value][1], '%d.%m.%Y')
        print(f'{arg.name.value} ma urodziny za {-(diff.days)} dni')

    @input_error
    def change_phone(self, arg, contacts_c):
        self.phone = arg.phone.value
        contacts_c.data[arg.name.value] = self.phone

    def add_birthday(self, arg, contacts_c):
        self.birthday = arg.birthday.value
        contacts_c.data[arg.name.value][1] = self.birthday

    @input_error
    def remove_phone(self, phone, contacts_c):
        if len(self.phone) == 1:
            self.phone = []
        else:
            contacts_c[self.name.value].remove(phone.value)
        


def main():
    start = input('Write "hello" to start the bot: ')
    contacts_c = AddressBook()
    if start.lower() == 'hello':
        rec = None
        print('bot started')
        while True:
            command_raw = input('How can i help you?: ')
            command_lower = command_raw.lower()
            if command_lower.startswith('dodaj'):
                splitted = command_raw.split(' ')
                if len(splitted) > 3:
                    bday = splitted[3]
                    rec = Record(Name(Field(splitted[1])), Phone(Field(splitted[2])), Birthday(Field(bday)))
                else:
                    rec = Record(Name(Field(command_raw.split(' ')[1])), Phone(Field(command_raw.split(' ')[2])))
                contacts_c.add_record(rec)
                pass

            elif command_lower.startswith('zmień'):
                rec = Record(Name(Field(command_raw.split(' ')[1])), Phone(Field(command_raw.split(' ')[2])))
                rec.change_phone(rec, contacts_c)
                pass

            elif command_lower.startswith('szukaj'):
                rec = Record(Name(Field(command_raw.split(' ')[1])))
                contacts_c.search(rec)

            elif command_lower.startswith('znajdź'):
                contacts_c.find(command_raw.split(' ')[1])

            elif command_lower.startswith('usuń kontakt'):
                rec = Record(Name(Field(command_raw.split(' ')[2])))
                contacts_c.data.pop(rec.name.value)

            elif command_lower.startswith('usuń telefon'):
                contact_name = command_raw.split(' ')[2]
                phone_number = command_raw.split(' ')[3]
                rec = Record(Name(Field(contact_name)))
                rec.remove_phone(Phone(Field(phone_number).value), contacts_c)

            elif command_lower.startswith('urodziny'):
                rec = Record(Name(Field(command_raw.split(' ')[1])), birthday=Birthday(Field(command_raw.split(' ')[2])))
                rec.add_birthday(rec, contacts_c)

            elif command_lower.startswith('kiedy'):
                rec = Record(Name(Field(command_raw.split(' ')[1])))
                rec.days_to_birthday(rec, datetime.now(), contacts_c)

            elif command_lower == 'pokaż':
                print(contacts_c)
                pass

            elif command_lower.startswith('iteruj'):
                for i in contacts_c.iterator(command_raw.split(' ')[1]):
                    print(i)
            
            elif command_lower.startswith('zapisz'):
                contacts_c.save_to_file(command_raw.split(' ')[1])

            elif command_lower.startswith('wczytaj'):
                contacts_c = contacts_c.read_from_file(Path(command_raw.split(' ')[1]))
                print(contacts_c)
            elif command_lower in ENDINGS:
                print('bot stopped')
                end()
                break
            else:
                print('Nie znam takiej komendy', command_raw)


if __name__ == '__main__':
    main()