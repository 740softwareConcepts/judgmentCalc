
@cli.command()
@click.option('--case-number', prompt='Enter case number to update', help='Case number to update')
def case_update(case_number):
    try:
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()

        if case_id:
            case_id = case_id[0]

            new_case_number = click.prompt('Enter new case number (2 letters, 8-10 characters)', type=str)
            if not (len(new_case_number) >= 8 and len(new_case_number) <= 10 and new_case_number[:2].isalpha()):
                click.echo("Case number must begin with 2 letters and have 8-10 characters.")
                return

            current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE CASES SET caseNumber = %s, updateDate = %s WHERE caseID = %s",
                           (new_case_number, current_date, case_id))
            conn.commit()
            click.echo(f"Case '{case_number}' updated to '{new_case_number}' with update date {current_date}.")
        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()