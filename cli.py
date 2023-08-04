
import argparse
from aissistant import search, index, get_profile, set_profile

def main():
    parser = argparse.ArgumentParser(description='Aissistant CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Get Profile Command
    get_profile_parser = subparsers.add_parser('get-profile')
    get_profile_parser.add_argument('field_name', nargs='?', default=None)

    # Set Profile Command
    set_profile_parser = subparsers.add_parser('set-profile')
    set_profile_parser.add_argument('field_name')
    set_profile_parser.add_argument('value')

    # Index Command
    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('prompt')
    index_parser.add_argument('response')

    # Search Command
    search_parser = subparsers.add_parser('search')
    search_parser.add_argument('query')

    args = parser.parse_args()

    if args.command == 'get-profile':
        print(get_profile(args.field_name))
    elif args.command == 'set-profile':
        set_profile(args.field_name, args.value)
        print(f'Profile updated: {args.field_name} = {args.value}')
    elif args.command == 'index':
        index(args.prompt, args.response)
        print(f'Indexed: {args.prompt} -> {args.response}')
    elif args.command == 'search':
        results = search(args.query)
        for result in results:
            print(result[0], result[1])
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
