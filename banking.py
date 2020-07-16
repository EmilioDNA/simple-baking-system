# Write your code here
import random
import sqlite3
from contextlib import contextmanager


DATABASE = 'card.s3db'
CREATE_CARD_TABLE_QUERY = '''
    CREATE TABLE IF NOT EXISTS card(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
    );
'''


# Define a context manager for handling db commands
@contextmanager
def open_sqlite3(db_path):
    # pre-processing
    conn = sqlite3.connect(db_path)
    yield conn.cursor()
    # post-processing
    conn.commit()
    conn.close()


def print_main_menu():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')


def print_secondary_menu():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('2. Log out')
    print('0. Exit')


def verify_account():
    print('Enter you card number:')
    card_n = input()
    print('Enter your PIN:')
    pin_n = input()
    return evaluate_select_card(card_n, pin_n, DATABASE)


def execute_query(sql_query_insert, db):
    with open_sqlite3(db) as c:
        c.execute(sql_query_insert)


def insert_query(number, pin, balance):
    sql_insert = f'''
        INSERT INTO card (number, pin, balance) 
        VALUES ('{number}', '{pin}', {balance})
    '''
    db = DATABASE
    execute_query(sql_insert, db)


def evaluate_select_card(number, pin, db):
    sql_select = f'''
        SELECT * FROM card 
        WHERE number='{number}' 
        AND pin='{pin}'
    '''
    with open_sqlite3(db) as c:
        c.execute(sql_select)
        data = c.fetchall()
        if len(data) == 1:
            return data[0]
        else:
            return None


def evaluate_transfer_card(number):
    sql_select = f'''
            SELECT * FROM card 
            WHERE number='{number}' 
        '''
    db = DATABASE
    with open_sqlite3(db) as c:
        c.execute(sql_select)
        data = c.fetchall()
        if len(data) == 1:
            return data[0]
        else:
            return None


def get_balance(number):
    sql_select = f'''
        SELECT balance FROM card
        WHERE number='{number}'
    '''
    db = DATABASE
    with open_sqlite3(db) as c:
        c.execute(sql_select)
        data = c.fetchone()
        return data


def add_income(number_a, income_up):
    sql_update = f'''
            UPDATE card 
            SET balance=(balance +{income_up})
            WHERE number='{number_a}'
        '''
    db = DATABASE
    execute_query(sql_update, db)


def delete_account(number_a):
    sql_delete = f'''
        DELETE FROM card
        WHERE number='{number_a}'
    '''
    db = DATABASE
    execute_query(sql_delete, db)


def generate_bank_account():
    inn = 400000
    can = random.randint(100000000, 999999999)
    cd = generate_checksum(str(inn) + str(can))
    pin = random.randint(1000, 9999)
    card_account = str(inn) + str(can) + str(cd)
    insert_query(card_account, pin, 0)
    return card_account, pin


def generate_checksum(partial_number):
    partial_list = []
    for i, num in enumerate(partial_number):
        int_num = int(num)
        if (i + 1) % 2 != 0:
            int_num *= 2
            if int_num > 9:
                int_num -= 9
        partial_list.append(int_num)
    total_sum = sum(partial_list)
    checksum = 10 - total_sum % 10
    return checksum


def check_luhn(credit_card_number):
    credit_card_list = [int(digit) for digit in str(credit_card_number)]
    print(credit_card_number)
    print(credit_card_list)
    # removing the last digit
    last_number = credit_card_list.pop()
    # double odd numbers
    new_credit_card_list = []
    for i, num in enumerate(credit_card_list):
        if (i + 1) % 2 != 0:
            num *= 2
            if num > 9:
                num -= 9
        new_credit_card_list.append(num)
    new_credit_card_list.append(last_number)
    print(new_credit_card_list)
    print(sum(new_credit_card_list))
    if sum(new_credit_card_list) % 10 == 0:
        return True
    return False


def display_generated_bank_account(card_account, pin):
    print('Your card has been created')
    print('Your card number')
    print(card_account)
    print('Your card PIN')
    print(pin)
    print()


# Create the database and the table if it does not exists
execute_query(CREATE_CARD_TABLE_QUERY, DATABASE)
choice = ''
exit_p = False
while not exit_p:
    print_main_menu()
    choice = input()
    if choice == '1':
        ca, p = generate_bank_account()
        display_generated_bank_account(ca, p)
    elif choice == '2':
        account = verify_account()
        if account is not None:
            print('You successfully logged in!')
            secondary_choice = ''
            while secondary_choice != '0':
                print_secondary_menu()
                secondary_choice = input()
                if secondary_choice == '1':
                    balance = account[3]
                    print(f'Balance: {balance}')
                elif secondary_choice == '2':
                    print('Enter income:')
                    income = input()
                    add_income(account[1], int(income))
                    print('Income was added!')
                elif secondary_choice == '3':
                    print('Transfer')
                    print('Enter card number:')
                    card_transfer = input()
                    if check_luhn(card_transfer):
                        card_verified = evaluate_transfer_card(card_transfer)
                        if card_verified is not None:
                            if card_verified[1] == account[1]:
                                print("You can't transfer money to the same account!")
                            else:
                                print('Enter how much money you want to transfer')
                                money_to_transfer = input()
                                current_balance = get_balance(account[1])
                                if current_balance[0] < int(money_to_transfer):
                                    print('Not enough money!')
                                else:
                                    add_income(account[1],  (-int(money_to_transfer)))
                                    add_income(card_verified[1], money_to_transfer)
                                    print('Success!')
                        else:
                            print('Such a card does not exist.')
                    else:
                        print('Probably you made mistake in the card number. Please try again!')
                elif secondary_choice == '4':
                    delete_account(account[1])
                    print('The account has been closed!')
                    secondary_choice = '0'
                elif secondary_choice == '5':
                    print('You have successfully logged out!')
                    secondary_choice = '0'
                elif secondary_choice == '0':
                    exit_p = True
        else:
            print('Wrong card number or PIN!')
    elif choice == '0':
        exit_p = True
