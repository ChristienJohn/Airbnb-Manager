import pyodbc
import datetime
import sys

#Create connection
#conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_ckjohn;pwd=AmJ2q47nmf7RaAQ7')



def Book_Listing():  #function to book listing

    #Create connection
    conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_ckjohn;pwd=AmJ2q47nmf7RaAQ7')

    cursor = conn.cursor() #creating cursor

    #get the appropriate data from user to book listing
    print("----------")
    Booking = input("Please input the id of the Listing you wish to book (Integer) : ")
    print("----------")
    name = input("Please input your name (String) : ")
    print("----------")
    start_date = input("When will you be staying from? (YYYY-MM-DD) : ")
    print("----------")
    end_date = input("When will you be staying to? (YYYY-MM-DD) : ")
    print("----------")
    num_guests = input("How many guests? (Integer) : ")
    print("----------")

    cursor.execute("select max(B.id)+1 from Bookings B") #grab the max id + 1
    results = cursor.fetchone()
    
    #insert data in Bookings table, trigger from assignment 4 handles updating Calendar table
    cursor.execute("""
    insert into Bookings(id, listing_id, guest_name, stay_from, stay_to, number_of_guests)
    values(?, ?, ?, ?, ?, ?)
    """, str(results[0]), Booking, name, start_date, end_date, num_guests)
    conn.commit()

    print("Listing Successfully Booked!")
    print("----------")

    conn.close()
    main() #go back to main, picking function




def Write_Review():     #function that allows users to write reviews

    #Create connection
    conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_ckjohn;pwd=AmJ2q47nmf7RaAQ7')

    cursor = conn.cursor() #creating cursor
    print("----------")
    user_name = input("Please input your name : ")
    print("----------")

    cursor.execute("""
    select B.id, B.listing_id
    from Bookings B
    where B.guest_name = ?
    """, user_name)

    results = cursor.fetchone()

    if cursor.rowcount == 0:    #check if user has booked the listing that they put in 
        print("----------")
        print("You currently have no Bookings")
        print("----------")
        main()


    while results:   #if cursor is not empty print all Bookings of the user
        print("----------")
        print("Booking Id: " + str(results[0]))
        print("Listing Id: " + str(results[1]))
        results = cursor.fetchone()
    print("----------")
    
    #grab all data needed for inserting review
    booking_id = input("Please enter the Booking Id of the Booking you wish to review : ")
    print("----------")

    #get the listing id of the booking that user selected
    cursor.execute("""
    select B.listing_id
    from Bookings B
    where B.guest_name = ? and
    B.id = ?
    """, user_name, booking_id)
    results = cursor.fetchone()

    if (cursor.rowcount == 0):
        print("You do not have bookings of that ID, Please try again")
        print("----------")
        main()
    
    review_text = input("Please enter your review : ")
    print("----------")
    

    cursor.execute("select max(R.id)+1 from Reviews R") #grab the max review id + 1
    reviews_id = cursor.fetchone()

    #insert the review using all the data collected
    SQLCommand = ("insert into Reviews(listing_id, id, comments, guest_name) values(?, ?, ?, ?)")
    values = [str(results[0]), str(reviews_id[0]), review_text, user_name]


    #Try and Except catches error if triggers happen
    try: 
        cursor.execute(SQLCommand, values)
        conn.commit()
        print("Review Worked!")
        print("----------")
    except pyodbc.ProgrammingError:
        print('It has not been the end of your booking date')
        print("----------")
        print('Review Unsuccessful')
        print("----------")
    finally:
        conn.close()  #close connection



    main() #go back to main, picking function



def Search_Listings():     #function to allow users to search for available listings

    #Create connection
    conn = pyodbc.connect('driver={SQL Server};server=cypress.csil.sfu.ca;uid=s_ckjohn;pwd=AmJ2q47nmf7RaAQ7')

    cursor = conn.cursor() #creating cursor

    #gets the minimum date in Calendar table
    min_date = """
        select min(C.date) from Calendar C;
        """
    #gets the maximum date in Calendar table
    max_date = """
        select max(C.date) from Calendar C;
        """
    cursor.execute(min_date) #get the earliest time in Calendar table
    results = cursor.fetchone()
    min_date_check = results[0]

    cursor.execute(max_date) #get the latest time in Calendar table
    results = cursor.fetchone()
    max_date_check = results[0]

    #ask the user the criteria to search for listings
    print("----------")
    min_price = input("Select Minimum Price, or \'None\' (Integer) : ") 
    if (min_price == "None"):   #If user doesnt put in min price put it as 0
        min_price = 0 
    print("----------")
    max_price = input("Select Maximum Price, or \'None\' (Integer) : ")
    if (max_price == "None"):   #If user doesnt put in max price put it as inf
        max_price = sys.maxsize
    print("----------")
    num_bedrooms = input("Select Number Of Bedrooms, or \'None\' (Integer) : ")
    print("----------")
    start_date = input('Enter a starting date in, or \'None\' (YYYY-MM-DD) : ')
    if (start_date == "None"):   #If user doesnt put in a start_date, use the minimum date in Calendar table as start_date
        start_date = min_date_check
    elif (start_date < min_date_check): #If user inputs start_date that is smaller than the earliest listing date available 
        print("----------")
        print("There are no listings within your start date, the earliest start date is : " + min_date_check)
        print("Please try again")
        main()
    print("----------")
    end_date = input('Enter an ending date in, or \'None\' (YYYY-MM-DD) : ')
    if (end_date == "None"):     #If user doesnt put in a end_date, use the maximum date in Calendar table as end_date
        end_date = max_date_check
    elif (end_date > max_date_check): #If user inputs start_date that is smaller than the earliest listing date available 
        print("----------")
        print("There are no listings within your end date, the latest end date is : " + max_date_check)
        print("Please try again")
        main()
    print("----------")
    #Note that if user doesnt specify dates, results of search will be very small since it is highly unlikely that a listing will be 
    #available for the span of the min and max dates!


    #if user DOES NOT input number of bedrooms (same query but doesnt check number of bedrooms)
    SQLCommand2 = """
    SELECT allProducts.listing_id, L.name, LEFT(L.description, 25), L.number_of_bedrooms, allProducts.sum_price
FROM Listings L,  
(
SELECT  listing_id,max(price) as max_price, sum(price) as sum_price
FROM Calendar
where date >= ? and date <= ?
group by  listing_id
) allProducts
WHERE allProducts.max_price >= ? and allProducts.max_price <= ? and
L.id = allProducts.listing_id and
allProducts.listing_id NOT IN (SELECT listing_id
FROM    
(
SELECT  listing_id
FROM Calendar
where date >= ? and date <= ? and available = 0
group by  listing_id
) all_Products);"""



    #this LONG sql query to get listings based on user input
    SQLCommand = """
    SELECT allProducts.listing_id, L.name, LEFT(L.description, 25), L.number_of_bedrooms, allProducts.sum_price
FROM Listings L,  
(
SELECT  listing_id,max(price) as max_price, sum(price) as sum_price
FROM Calendar
where date >= ? and date <= ?
group by  listing_id
) allProducts
WHERE allProducts.max_price >= ? and allProducts.max_price <= ? and
L.id = allProducts.listing_id and
L.number_of_bedrooms = ? and
allProducts.listing_id NOT IN (SELECT listing_id
FROM    
(
SELECT  listing_id
FROM Calendar
where date >= ? and date <= ? and available = 0
group by  listing_id
) all_Products);"""

    
    if (num_bedrooms == "None"):
        cursor.execute(SQLCommand2, (start_date, end_date, min_price, max_price, start_date, end_date))
    else:
        cursor.execute(SQLCommand, (start_date, end_date, min_price, max_price, num_bedrooms, start_date, end_date))

    results = cursor.fetchone()
    if cursor.rowcount == 0:    #if cursor is empty, prompt user to try again
        print("----------")
        print("There are no Listings that you are looking for. Please try again")
        print("----------")
        main()
    while results:   #if cursor is not empty print appropiate data per listing
        print("----------")
        print("Id: " + str(results[0]))
        print("Name: " + str(results[1]))
        print("Description: " + str(results[2]))
        print("Number of Bedrooms: " + str(results[3]))
        print("Total Price: " + str(results[4]))
        #print("Date: " + str(results[5]))
        #print("Available?: " + str(results[6]))
        results = cursor.fetchone()
    print("----------")

    conn.close()

    #After user searched for listings, give choice to book listing or go back to main menu
    user_choice = input("Please choose one: \'Book Listing\' or \'Main Menu\':\n")
    while user_choice not in ("Book Listing", "Main Menu"):
        user_choice = input("Please enter: \'Book Listing\' or \'Main Menu\':\n")
    if (user_choice == "Book Listing"):
        Book_Listing()
    elif (user_choice == "Main Menu"):
        main()
    
    #main()   #go back to main function



#Main function asks user what they want to do and runs function based on what they choose
def main():
    print("----------")
    #ask user what they want to do
    #--BOOK LISTING IS ONLY POSSIBLE AFTER USER SEARCHES--#
    val = input("Pick one: \'Search Listings\', \'Write Review\':\n")

    #if user inputs incorrectly, keep asking
    while val not in ("Search Listings", "Write Review"):
        val = input("Please enter: \'Search Listings\' or \'Write Review\':\n")

    #depending on user input, run the function
    if (val == "Search Listings"):
        Search_Listings()
    elif (val == "Write Review"):
        Write_Review()



main() #start program

