import sqlite3
import os


# =========================================================
# PROJECT ROOT
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# FIND DATABASE FILE
# =========================================================

def find_documents_database():

    database_candidates = []

    print()
    print("========================================")
    print("SEARCHING FOR DATABASE")
    print("========================================")
    print()

    for root, dirs, files in os.walk(PROJECT_ROOT):

        # Ignore virtual environments and cache folders
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in {
                ".venv",
                "venv",
                "__pycache__",
                ".git"
            }
        ]

        for filename in files:

            if not filename.lower().endswith(".db"):
                continue

            full_path = os.path.join(
                root,
                filename
            )

            database_candidates.append(
                full_path
            )


    if not database_candidates:

        print("❌ No .db database files found.")
        print()
        print(
            "Please check where your SQLite database is stored."
        )

        raise SystemExit(1)


    print("Database files found:")
    print()

    for index, path in enumerate(
        database_candidates,
        start=1
    ):

        print(
            f"{index}. {os.path.relpath(path, PROJECT_ROOT)}"
        )


    print()
    print("Checking which database contains 'documents' table...")
    print()


    documents_databases = []


    for database_path in database_candidates:

        try:

            connection = sqlite3.connect(
                database_path
            )

            cursor = connection.cursor()

            cursor.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='documents'
            """)

            result = cursor.fetchone()

            connection.close()


            if result:

                documents_databases.append(
                    database_path
                )

        except Exception as error:

            print(
                f"⚠️ Could not inspect: {database_path}"
            )

            print(
                f"   Reason: {error}"
            )


    if not documents_databases:

        print()
        print(
            "❌ None of the database files contains "
            "a 'documents' table."
        )

        raise SystemExit(1)


    if len(documents_databases) > 1:

        print()
        print(
            "⚠️ Multiple databases contain a "
            "'documents' table:"
        )

        for path in documents_databases:

            print(
                f"   - {path}"
            )

        print()
        print(
            "Please check the database configuration "
            "before continuing."
        )

        raise SystemExit(1)


    selected_database = documents_databases[0]


    print(
        "✅ Correct database found:"
    )

    print(
        f"   {selected_database}"
    )

    print()


    return selected_database


# =========================================================
# FIND DATABASE
# =========================================================

DB_PATH = find_documents_database()


# =========================================================
# CONNECT DATABASE
# =========================================================

print("Connecting to database...")

connection = sqlite3.connect(
    DB_PATH
)

cursor = connection.cursor()


# =========================================================
# GET EXISTING COLUMNS
# =========================================================

cursor.execute(
    "PRAGMA table_info(documents)"
)

columns = cursor.fetchall()


existing_columns = {
    column[1]
    for column in columns
}


print()
print("========================================")
print("EXISTING DOCUMENT COLUMNS")
print("========================================")
print()


for column in existing_columns:

    print(
        f"✓ {column}"
    )


# =========================================================
# ADD page_count
# =========================================================

print()
print("========================================")
print("ADDING NEW COLUMNS")
print("========================================")
print()


if "page_count" not in existing_columns:

    cursor.execute("""
        ALTER TABLE documents
        ADD COLUMN page_count INTEGER
    """)

    print(
        "✅ Added: page_count"
    )

else:

    print(
        "✓ page_count already exists"
    )


# =========================================================
# ADD page_count_exact
# =========================================================

if "page_count_exact" not in existing_columns:

    cursor.execute("""
        ALTER TABLE documents
        ADD COLUMN page_count_exact BOOLEAN
    """)

    print(
        "✅ Added: page_count_exact"
    )

else:

    print(
        "✓ page_count_exact already exists"
    )


# =========================================================
# ADD page_count_label
# =========================================================

if "page_count_label" not in existing_columns:

    cursor.execute("""
        ALTER TABLE documents
        ADD COLUMN page_count_label VARCHAR(100)
    """)

    print(
        "✅ Added: page_count_label"
    )

else:

    print(
        "✓ page_count_label already exists"
    )


# =========================================================
# SAVE
# =========================================================

connection.commit()


# =========================================================
# VERIFY
# =========================================================

cursor.execute(
    "PRAGMA table_info(documents)"
)

columns_after = cursor.fetchall()


columns_after_names = {
    column[1]
    for column in columns_after
}


print()
print("========================================")
print("DATABASE MIGRATION COMPLETED")
print("========================================")
print()


required_columns = [
    "page_count",
    "page_count_exact",
    "page_count_label"
]


for column in required_columns:

    if column in columns_after_names:

        print(
            f"✅ {column}"
        )

    else:

        print(
            f"❌ {column} NOT FOUND"
        )


# =========================================================
# CLOSE DATABASE
# =========================================================

connection.close()


print()
print("========================================")
print("DONE")
print("========================================")
print()

print(
    "Database migration completed successfully."
)

print(
    "You can now start Flask again."
)

print()