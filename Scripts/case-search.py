
@cli.command()
@click.option('--case-number', prompt='Enter partial case number to search', help='Partial case number to search')
@click.option('--start-date', help='Start date (YYYY-MM-DD) to filter cases')
@click.option('--end-date', help='End date (YYYY-MM-DD) to filter cases')
def case_search(case_number, start_date, end_date):
    try:
        query = "SELECT * FROM CASES WHERE caseNumber LIKE %s"
        params = ('%' + case_number + '%',)

        if start_date and end_date:
            start_datetime = dt.strptime(start_date, '%Y-%m-%d')
            end_datetime = dt.strptime(end_date, '%Y-%m-%d')
            query += " AND createDate BETWEEN %s AND %s"
            params += (start_datetime, end_datetime)

        cursor.execute(query, params)
        cases = cursor.fetchall()

        if cases:
            click.echo("Matching cases:")
            for case in cases:
                # Display the case details, modify this part based on your table structure
                click.echo(f"Case Number: {case[1]}")  # Assuming caseNumber is at index 1
                click.echo(f"Create Date: {case[2]}")  # Assuming createDate is at index 2
                click.echo(f"Update Date: {case[3]}")  # Assuming updateDate is at index 3
                # Add other attributes as needed
        else:
            click.echo(f"No matching cases found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()