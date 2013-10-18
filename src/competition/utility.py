from django.db.models import Q


def competitor_search_filter(queryset, search):
    # Split the full name on spaces
    if search != None:
        search = search.split(" ")
    else:
        search = []

    # Create queries to check username, first_name, and last_name
    query = [Q(username__icontains=part) |
             Q(first_name__icontains=part) |
             Q(last_name__icontains=part) for part in search]

    # Combine the queries into one monster query
    query = reduce(lambda x, y: x | y, query)

    # Execute the query and return only unique results
    return queryset.filter(query).distinct()
