import sqlite3

try:
    import tkinter
except ImportError:  # python 2 only
    import Tkinter as tkinter


class Scroll_Box(tkinter.Listbox):

    """Overwriting the init method to add a scrollbar field after calling the super.init
    method."""
    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)  # super init method

        self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)
        ## 12/17/20: this is the creation of the scrollbar field
        ## 12/17/20: now we need to change our listbox types to scrollbox

    """Overriding the grid manager"""
    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set
        # All the options we have included in our definition of this method won't be
        # present in kwargs. Any additional options that the calling code uses will
        # just be passed on to the super classes grid method.


class DataListbox(Scroll_Box):  # inheriting from Scroll_Box

    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)  # calling the super method for Scroll_Box
        # sort_order() argument, we have to find that as a tuple to allow the caller to specify
        # multiple columns to sort on if they need to.

        self.linked_box = None
        self.link_field = None

        # We are creating data attributes from the parameters passed to the init method
        self.cursor = connection.cursor()  # storing the actual cursor
        self.table = table  # table we are selecting data from
        self.field = field
        # calling the column parameter, 'field', because we are working in the grid
        # layout manager, and 'column' could then get confusing for that reason.

        self.bind('<<ListboxSelect>>', self.on_select)

        self.sql_select = "SELECT " + self.field + ", _id" + " FROM " + self.table
        if sort_order:
            self.sql_sort = " ORDER BY " + ','.join(sort_order)
        else:
            self.sql_sort = " ORDER BY " + self.field


    def clear(self):
        """If we're going to allow the list boxes to be requeried, so that they can show new
        data, we need some way to clear the existing data out..This clear method will do
        just that."""
        self.delete(0, tkinter.END)


    def link(self, widget, link_field):
        self.linked_box = widget
        widget.link_field = link_field  # basically saving the value that was passed in the argument


    def requery(self, link_value=None):
        """Going to requery data after clear method clears out existing data.
        12/23/20: given a single parameter which will be the ID to match, and default to None
        so that we can populate a list with all records as we did for the artists."""
        if link_value and self.link_field:
            sql = self.sql_select + " WHERE " + self.link_field + "=?" + self.sql_sort
            print(sql)  # TODO delete this line
            self.cursor.execute(sql, (link_value,))
        else:
            print(self.sql_select + self.sql_sort)  # TODO delete this line
            self.cursor.execute(self.sql_select + self.sql_sort)  # executing query

        self.clear()  # clear the listbox contents before re-loading
        for value in self.cursor:
            self.insert(tkinter.END, value[0])  # looping through the values one by one
            # and then actually adding each one to the listbox. We get a tuple representing
            # each row. As our query specified the column we want, and the id, we add th first
            # item from the tuple into the list and that's why we use the value 0.

        if self.linked_box:
            self.linked_box.clear()


    def on_select(self, event):
        """When an artist is selected, the album choices will appear according to the
        artist selected"""
        if self.linked_box:
            print(self is event.widget)     # TODO delete this line
            index = self.curselection()[0]  # this is currently set up to only allow selection of one item at a time.
            value = self.get(index),  # this is a tuple

            link_id = self.cursor.execute(self.sql_select + " WHERE " + self.field + "=?", value).fetchone()[1]
            # this sql statement returns all the columns we're displaying
            self.linked_box.requery(link_id)

        # get the artist ID from the database row
        # artist_id = connect.execute("SELECT artists._id FROM artists WHERE artists.name=?", artist_name).fetchone()
        # alist = []
        # for row in connect.execute("SELECT albums.name FROM albums WHERE albums.artist = ? ORDER BY albums.name", artist_id):
        #     # querying the database to retrieve the artist ID
        #     alist.append(row[0])  # appending the names to a list
        # albums_LV.set(tuple(alist))
        #
        # # This will reset/clear the songs list if you select a different artist
        # songs_LV.set(("Choose an album",))

# def get_songs(event):
#     """When an album is selected the songs choice will then appear according to the
#     album selected. This function will be bound to the album listbox"""
#     lb = event.widget
#     index = int(lb.curselection()[0])
#     album_name = lb.get(index),
#
#     # get the artist ID from the database row
#     album_id = connect.execute("SELECT albums._id FROM albums WHERE albums.name=?", album_name).fetchone()
#     alist = []
#     for x in connect.execute("SELECT songs.title FROM songs WHERE songs.album=? ORDER BY songs.track", album_id):
#         alist.append(x[0])
#     songs_LV.set(tuple(alist))

if __name__ == '__main__':
    connect = sqlite3.connect('music.sqlite')

    main_window = tkinter.Tk()
    main_window.title('Music Database Browser')
    main_window.geometry('1024x768')


    ##COLUMNS##
    # creates our columns
    main_window.columnconfigure(0, weight=2)
    main_window.columnconfigure(1, weight=2)
    main_window.columnconfigure(2, weight=2)
    main_window.columnconfigure(3, weight=1)  # spacer column on far right


    ##ROWS##
    # creates our rows
    main_window.rowconfigure(0, weight=1)
    main_window.rowconfigure(1, weight=5)  # contains list box
    main_window.rowconfigure(2, weight=5)  # contains list box
    main_window.rowconfigure(3, weight=1)  # spacer row at bottom of window


    ##LABELS##
    # creates and adds labels to the grid/window
    tkinter.Label(main_window, text="Artists").grid(row=0, column=0)
    tkinter.Label(main_window, text="Albums").grid(row=0, column=1)
    tkinter.Label(main_window, text="Songs").grid(row=0, column=2)


    ##ARTISTS LIST BOX##
    """creates artist list and adds to the grid/window"""
    ## 12/17/20: artist_list = tkinter.Listbox(main_window)
    # we now have the Scroll_Box class which includes tkinter.Scrollbar()
    # artist_list = Scroll_Box(main_window)
    artist_list = DataListbox(main_window, connect, "artists", "name")
    artist_list.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(30, 0))
    artist_list.config(border=2, relief='sunken')

    # for artist in connect.execute("SELECT artists.name FROM artists ORDER BY artists.name"):
    #     artist_list.insert(tkinter.END, artist[0])
    artist_list.requery()

    # whenever an item is selected in the artist list, we're going to get our get_albums method to be called

    ## creates scroll bar in artist list box and adds to the grid/window
    ## yview tells it to scroll in the y-direction
    # artist_scroll = tkinter.Scrollbar(main_window, orient=tkinter.VERTICAL, command=artist_list.yview)
    # artist_scroll.grid(row=1, column=0, sticky='nse', rowspan=2)
    # artist_list['yscrollcommand'] = artist_scroll.set
    ## 12/17/20: We don't need 69-71 now because we have created the grid() method

    ##ALBUMS LIST BOX##
    """creates albums list and adds to the grid/window"""
    albums_LV = tkinter.Variable(main_window)
    albums_LV.set(("Choose an album:",))

    ## 12/17/20: albums_list = tkinter.Listbox(main_window, listvariable=albums_LV)
    # the variable albums_LV is bound to the Listbox
    # we now have Scroll_Box class which includes tkinter.Scrollbar()
    # albums_list = Scroll_Box(main_window, listvariable=albums_LV)
    albums_list = DataListbox(main_window, connect, "albums", "name", sort_order=("name", ))
    # albums_list.requery(12)
    albums_list.grid(row=1, column=1, sticky='nsew', padx=(30, 0))
    albums_list.config(border=2, relief='sunken')

    artist_list.link(albums_list, "artist")
    # albums_list.bind('<<ListboxSelect>>', get_songs)  # functions parameter = get_songs
    # albums_scroll = tkinter.Scrollbar(main_window, orient=tkinter.VERTICAL, command=albums_list.yview)
    # albums_scroll.grid(row=1, column=1, sticky='nse', rowspan=1)
    # albums_list['yscrollcommand'] = albums_scroll.set
    ## 12/17/20: We don't need 69-71 now because we have created the grid() method


    ##SONGS LIST BOX##
    """creates songs list and adds to the grid/window"""
    songs_LV = tkinter.Variable(main_window)
    songs_LV.set(("Choose a song:",))

    ## 12/17/20: songs_list = tkinter.Listbox(main_window, listvariable=songs_LV)
    # we now have Scroll_Box class which includes tkinter.Scrollbar()
    # songs_list = Scroll_Box(main_window, listvariable=songs_LV)
    songs_list = DataListbox(main_window, connect, "songs", "title", ("track", "title"))
    # songs_list.requery()
    songs_list.grid(row=1, column=2, sticky='nsew', padx=(30, 0))
    songs_list.config(border=2, relief='sunken')

    albums_list.link(songs_list, "album")

    ##MAIN LOOP##
    # test_list = range(0, 100)
    # albums_LV.set(tuple(test_list))

    main_window.mainloop()
    print("Closing database connection")  # prints when you close database window
    connect.close()




