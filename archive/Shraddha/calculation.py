from datetime import datetime

DEFAULT_ADDITIONAL_POINTS = 0.0

# Function to parse the date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return None

# Function to calculate interest
def calculate_interest(principal, due_date, rate, period, interest_type):
    today = datetime.now()

    if due_date is None:
        delta = 0
    else:
        delta = (today - due_date).days

    if interest_type == 'simple':
        interest = principal * rate * delta / 365
    elif interest_type == 'compound':
        if period == 'per annum':
            n = 1
        elif period == 'monthly':
            n = 12
        elif period == 'per diem':
            n = 365
        elif period == 'weekly':
            n = 52
        interest = principal * (1 + rate / n) ** (n * delta / 365) - principal

    return interest

# Function to calculate contractual interest based on user input
def calculate_contractual_interest(case_number):
    # Collect user input for judgment details
    judgment_date_input = input("Has a judgment been entered? (yes/no): ").lower()

    if judgment_date_input == 'yes':
        judgment_date = parse_date(input("Enter the judgment date (YYYY-MM-DD): "))
    else:
        judgment_date = None

    # Collect additional user input
    interest_type = input("Enter interest type (simple/compound): ").lower()

    if interest_type not in ['simple', 'compound']:
        print("Invalid interest type. Please enter either 'simple' or 'compound'.")
        return

    # If interest type is compound, ask for compounding period
    if interest_type == 'compound':
        compounding_period = input("Enter the compounding period (per annum, monthly, per diem, weekly): ")
    else:
        compounding_period = None

    # Collect additional user input for liability name
    liability_name = input("Enter the name of the liability: ")

    principal_amount = float(input("Enter the principal amount: "))
    start_date = parse_date(input("Enter the start date (YYYY-MM-DD): "))
    end_date = parse_date(input("Enter the end date (YYYY-MM-DD): "))
    interest_rate = float(input("Enter the interest rate (%): ")) / 100

    # Calculate interest using the provided function
    total_interest = calculate_interest(principal_amount, judgment_date or start_date, interest_rate, compounding_period, interest_type)

    # Display the result
    print(f"Case Number: {case_number}")
    print(f"Liability Name: {liability_name}")
    print(f"Principal Amount: {principal_amount}")
    print(f"Interest Rate ({interest_type.capitalize()}): {interest_rate}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Total {interest_type.capitalize()} Interest: {total_interest}")
    print()

# Function to calculate statutory interest based on user input
def calculate_statutory_interest(case_number):
    # Collect additional user input for liability name
    liability_name = input("Enter the name of the liability: ")

    # Collect user input for statutory interest
    additional_points = float(input("Enter additional points above the prime rate (default is 0.0): ") or DEFAULT_ADDITIONAL_POINTS)

    # Fetch interest rate from the interest table in the database
    interest_rate = float(input("Enter interest rate from the interest table in the database (in percentage): ")) / 100

    # Collect additional user input
    interest_type = input("Enter interest type (simple/compound): ").lower()

    if interest_type not in ['simple', 'compound']:
        print("Invalid interest type. Please enter either 'simple' or 'compound'.")
        return

    # If interest type is compound, ask for compounding period
    if interest_type == 'compound':
        compounding_period = input("Enter the compounding period (per annum, monthly, per diem, weekly): ")
    else:
        compounding_period = None

    principal_amount = float(input("Enter the principal amount: "))
    start_date = parse_date(input("Enter the start date (YYYY-MM-DD): "))
    end_date = parse_date(input("Enter the end date (YYYY-MM-DD): "))

    # Calculate interest using the provided function
    total_interest = calculate_interest(principal_amount, None, interest_rate + additional_points, compounding_period, interest_type)

    # Display the result
    print(f"Case Number: {case_number}")
    print(f"Liability Name: {liability_name}")
    print(f"Principal Amount: {principal_amount}")
    print(f"Interest Rate ({interest_type.capitalize()}): {interest_rate + additional_points}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")
    print(f"Total {interest_type.capitalize()} Interest: {total_interest}")
    print()

# Function to identify and calculate interest based on user input
def identify_interest():
    # Ask for case number
    case_number = input("Enter the case number: ")

    while True:
        # Prompt the user to input whether there is interest associated with the liability item
        has_interest = input("Is there interest associated with the liability item? (yes/no): ").lower()

        if has_interest == 'yes':
            # Prompt the user to choose between contractual and statutory interest
            interest_type = input("Choose interest type (contractual/statutory): ").lower()

            if interest_type == 'contractual':
                calculate_contractual_interest(case_number)
            elif interest_type == 'statutory':
                calculate_statutory_interest(case_number)
            else:
                print("Invalid interest type. Please enter either 'contractual' or 'statutory'.")
        else:
            print("No interest associated with the liability item.")
            break

        # Ask if the user wants to calculate interest for another liability
        calculate_another = input("Do you want to calculate interest for another liability? (yes/no): ").lower()
        if calculate_another != 'yes':
            break

# Example usage:
identify_interest()