import sqlite3

try:
    import tkinter
except ImportError:  # python 2 only
    import Tkinter as tkinter


class Scroll_Box(tkinter.Listbox):

    """Overwriting the init method to add a scrollbar field after calling the super.init
    method."""
    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)

    """Overriding the grid manager"""
    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan)
        self['yscrollcommand'] = self.scrollbar.set


class DataListbox(Scroll_Box):

    def __init__(self, window, connection, table, field, sort_order=(), **kwargs):
        super().__init__(window, **kwargs)

        self.linked_box = None
        self.link_field = None
        self.link_value = None

        self.cursor = connection.cursor()
        self.table = table
        self.field = field

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
        widget.link_field = link_field


    def requery(self, link_value=None):
        """Going to requery data after clear method clears out existing data.
        12/23/20: given a single parameter which will be the ID to match, and default to None
        so that we can populate a list with all records as we did for the artists."""
        self.link_value = link_value  # store the id so we know the "master" record we're populated from
        if link_value and self.link_field:
            sql = self.sql_select + " WHERE " + self.link_field + "=?" + self.sql_sort
            print(sql)  # TODO delete this line
            self.cursor.execute(sql, (link_value,))
        else:
            print(self.sql_select + self.sql_sort)  # TODO delete this line
            self.cursor.execute(self.sql_select + self.sql_sort)

        self.clear()
        for value in self.cursor:
            self.insert(tkinter.END, value[0])

        if self.linked_box:
            self.linked_box.clear()


    def on_select(self, event):
        """When an artist is selected, the album choices will appear according to the
        artist selected"""
        if self.linked_box and self.curselection():
            print(self is event.widget)     # TODO delete this line
            index = self.curselection()[0]
            value = self.get(index),

            # get the id from the database row
            # make sure we're getting the correct one, by including the link_value if appropriate
            if self.link_value:
                value = value[0], self.link_value  # value is a tuple, and tuples are immutable
                sql_where = " WHERE " + self.field + "=? AND " + self.link_field + "=?"
            else:
                sql_where = " WHERE " + self.field + "=?"

            link_id = self.cursor.execute(self.sql_select + sql_where, value).fetchone()[1]
            self.linked_box.requery(link_id)


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
    main_window.columnconfigure(3, weight=1)


    ##ROWS##
    # creates our rows
    main_window.rowconfigure(0, weight=1)
    main_window.rowconfigure(1, weight=5)
    main_window.rowconfigure(2, weight=5)
    main_window.rowconfigure(3, weight=1)


    ##LABELS##
    # creates and adds labels to the grid/window
    tkinter.Label(main_window, text="Artists").grid(row=0, column=0)
    tkinter.Label(main_window, text="Albums").grid(row=0, column=1)
    tkinter.Label(main_window, text="Songs").grid(row=0, column=2)


    ##ARTISTS LIST BOX##
    """creates artist list and adds to the grid/window"""
    artist_list = DataListbox(main_window, connect, "artists", "name")
    artist_list.grid(row=1, column=0, sticky='nsew', rowspan=2, padx=(30, 0))
    artist_list.config(border=2, relief='sunken')

    artist_list.requery()

    ##ALBUMS LIST BOX##
    """creates albums list and adds to the grid/window"""
    albums_LV = tkinter.Variable(main_window)
    albums_LV.set(("Choose an album:",))

    albums_list = DataListbox(main_window, connect, "albums", "name", sort_order=("name", ))
    albums_list.grid(row=1, column=1, sticky='nsew', padx=(30, 0))
    albums_list.config(border=2, relief='sunken')

    artist_list.link(albums_list, "artist")


    ##SONGS LIST BOX##
    """creates songs list and adds to the grid/window"""
    songs_LV = tkinter.Variable(main_window)
    songs_LV.set(("Choose a song:",))

    songs_list = DataListbox(main_window, connect, "songs", "title", ("track", "title"))
    songs_list.grid(row=1, column=2, sticky='nsew', padx=(30, 0))
    songs_list.config(border=2, relief='sunken')

    albums_list.link(songs_list, "album")

    ##MAIN LOOP##

    main_window.mainloop()
    print("Closing database connection")
    connect.close()




