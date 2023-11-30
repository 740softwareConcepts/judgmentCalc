   
@cli.command()
@click.option('--case-number', prompt='Enter case number', help='Case number to remove')
@click.confirmation_option(prompt='Are you sure you want to remove this case?')
@click.option('--remove-clients', is_flag=True, default=False, help='Remove associated clients')
@click.option('--remove-liabilities', is_flag=True, default=False, help='Remove associated liabilities')
def case_remove(case_number, remove_clients, remove_liabilities):
    """This is a mini documenation for the command"""
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")  # Disable foreign key checks
        cursor.execute("SELECT caseID FROM CASES WHERE caseNumber = %s", (case_number,))
        case_id = cursor.fetchone()
        if case_id:
            case_id = case_id[0]
            if remove_clients:
                cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (case_id,))
                conn.commit()
                click.echo(f"All clients associated with case '{case_number}' removed.")
            if remove_liabilities:
                cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (case_id,))
                conn.commit()
                click.echo(f"All liabilities associated with case '{case_number}' removed.")
            cursor.execute("DELETE FROM CASES WHERE caseID = %s", (case_id,))
            conn.commit()
            click.echo(f"Case '{case_number}' removed.")
        else:
            click.echo(f"Case '{case_number}' not found.")
    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")  # Re-enable foreign key checks
        conn.close()