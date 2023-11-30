

@cli.command()
@click.option('--list', is_flag=True, default=False, help='List orphaned entries without deletion')
@click.option('--show-attributes', is_flag=True, default=False, help='Show attributes of orphaned entries')
@click.option('--remove', is_flag=True, default=False, help='Remove orphaned entries')
def orphaned_entries(list, show_attributes,remove):
    """This is a mini documenation for the command"""
    try:
        if list:
            cursor.execute("""
                SELECT c.* 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.* 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries found:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(entry)

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(entry)

        if show_attributes:
            cursor.execute("""
                SELECT c.* 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.* 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries and their attributes:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(f"CLIENTS entry: {entry}")

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(f"ACCOUNTING entry: {entry}")



        if remove:
            cursor.execute("""
                SELECT c.caseID 
                FROM CLIENTS c
                LEFT JOIN CASES cs ON c.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_clients = cursor.fetchall()

            cursor.execute("""
                SELECT a.caseID 
                FROM ACCOUNTING a
                LEFT JOIN CASES cs ON a.caseID = cs.caseID
                WHERE cs.caseID IS NULL
            """)
            orphaned_accounting = cursor.fetchall()

            if not orphaned_clients and not orphaned_accounting:
                click.echo("No orphaned entries found in CLIENTS and ACCOUNTING tables.")
            else:
                click.echo("Orphaned entries found:")
                if orphaned_clients:
                    click.echo("Orphaned entries in CLIENTS table:")
                    for entry in orphaned_clients:
                        click.echo(f"CLIENTS entry with caseID: {entry[0]}")
                    if click.confirm('Do you want to remove orphaned CLIENTS entries?', default=True):
                        for entry in orphaned_clients:
                            cursor.execute("DELETE FROM CLIENTS WHERE caseID = %s", (entry[0],))
                        conn.commit()
                        click.echo("Orphaned CLIENTS entries deleted.")

                if orphaned_accounting:
                    click.echo("Orphaned entries in ACCOUNTING table:")
                    for entry in orphaned_accounting:
                        click.echo(f"ACCOUNTING entry with caseID: {entry[0]}")
                    if click.confirm('Do you want to remove orphaned ACCOUNTING entries?', default=True):
                        for entry in orphaned_accounting:
                            cursor.execute("DELETE FROM ACCOUNTING WHERE caseID = %s", (entry[0],))
                        conn.commit()
                        click.echo("Orphaned ACCOUNTING entries deleted.")

    except mysql.connector.Error as err:
        click.echo(f"Error: {err}")
    finally:
        conn.close()