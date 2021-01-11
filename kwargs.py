# def print_backwards(*args, file=None):
#     for word in args[::-1]:
#         print(word[::-1], end=' ', file=file)
#
#
# with open("backwards.txt", 'w') as backwards:  # created and writing to a file called backwards.txt
#     print_backwards("hello", "earth", "take", "me", "to", "your", "leader", file=backwards)


# def print_backwards(*args, end=' ', **kwargs):
#     print(kwargs)
#     for word in args[::-1]:
#         print(word[::-1], end=' ', **kwargs)


def print_backwards(*args, end=' ', **kwargs):
    end_character = kwargs.pop('end', '\n')
    sep_character = kwargs.pop('sep', ' ')
    for word in args[::-1]:
        print(word[::-1], end=sep_character, **kwargs)
    print(end=end_character)


with open("backwards.txt", 'w') as backwards:  # created and writing to a file called backwards.txt
    print_backwards("hello", "earth", "take", "me", "to", "your", "leader", end='\n')
    print("another string")


print()
print("hello", "earth", "take", "me", "to", "your", "leader", end='\n', sep='|')
print_backwards("hello", "earth", "take", "me", "to", "your", "leader", end='\n', sep='|')
