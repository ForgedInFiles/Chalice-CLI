"""
Chalice Agent Marketplace CLI
Command-line interface for the agent marketplace
"""
import argparse
import json
from pathlib import Path
from typing import Optional
from .marketplace import get_marketplace


def cmd_search(args):
    """Search for agents"""
    marketplace = get_marketplace()

    tags = args.tags.split(',') if args.tags else None
    results = marketplace.search_agents(
        query=args.query or "",
        category=args.category,
        tags=tags,
        min_rating=args.min_rating,
        sort_by=args.sort
    )

    if not results:
        print("No agents found matching your criteria.")
        return

    print(f"\nFound {len(results)} agent(s):\n")
    for agent in results:
        print(f"📦 {agent.name} v{agent.version}")
        print(f"   ID: {agent.id}")
        print(f"   Author: {agent.author}")
        print(f"   Category: {agent.category}")
        print(f"   Rating: {'⭐' * int(agent.rating)} ({agent.rating}/5.0)")
        print(f"   Downloads: {agent.downloads}")
        print(f"   Description: {agent.description}")
        if agent.tags:
            print(f"   Tags: {', '.join(agent.tags)}")
        print()


def cmd_install(args):
    """Install an agent"""
    marketplace = get_marketplace()

    result = marketplace.install_agent(args.agent_id, force=args.force)

    if result['success']:
        print(f"✓ {result['message']}")
        print(f"  Installed to: {result['installed_path']}")
    else:
        print(f"✗ Error: {result['error']}")


def cmd_uninstall(args):
    """Uninstall an agent"""
    marketplace = get_marketplace()

    result = marketplace.uninstall_agent(args.agent_id)

    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ Error: {result['error']}")


def cmd_info(args):
    """Show agent information"""
    marketplace = get_marketplace()

    agent = marketplace.get_agent(args.agent_id)
    if not agent:
        print(f"✗ Agent not found: {args.agent_id}")
        return

    print(f"\n📦 {agent.name} v{agent.version}")
    print(f"{'=' * 60}")
    print(f"ID:           {agent.id}")
    print(f"Author:       {agent.author}")
    print(f"Category:     {agent.category}")
    print(f"Rating:       {'⭐' * int(agent.rating)} ({agent.rating}/5.0)")
    print(f"Downloads:    {agent.downloads}")
    print(f"Created:      {agent.created_at}")
    print(f"Updated:      {agent.updated_at}")
    print(f"\nDescription:\n{agent.description}")

    if agent.tags:
        print(f"\nTags: {', '.join(agent.tags)}")

    if agent.capabilities:
        print("\nCapabilities:")
        for cap in agent.capabilities:
            print(f"  • {cap}")

    if agent.dependencies:
        print("\nDependencies:")
        for dep in agent.dependencies:
            print(f"  • {dep}")

    # Show reviews
    reviews = marketplace.get_reviews(agent.id)
    if reviews:
        print(f"\nReviews ({len(reviews)}):")
        for review in reviews[:5]:  # Show first 5
            print(f"  {'⭐' * review.rating} by {review.user}")
            print(f"  {review.comment}")
            print()


def cmd_review(args):
    """Add a review for an agent"""
    marketplace = get_marketplace()

    result = marketplace.add_review(
        agent_id=args.agent_id,
        user=args.user,
        rating=args.rating,
        comment=args.comment
    )

    if result['success']:
        print(f"✓ Review added successfully!")
        print(f"  New rating: {result['new_rating']}/5.0")
    else:
        print(f"✗ Error: {result['error']}")


def cmd_list(args):
    """List installed agents or categories"""
    marketplace = get_marketplace()

    if args.categories:
        categories = marketplace.list_categories()
        print("\nAvailable categories:")
        for cat in categories:
            print(f"  • {cat}")
    else:
        installed = marketplace.list_installed()
        if not installed:
            print("\nNo agents installed.")
        else:
            print(f"\nInstalled agents ({len(installed)}):")
            for agent in installed:
                print(f"  • {agent}")


def cmd_publish(args):
    """Publish an agent to the marketplace"""
    marketplace = get_marketplace()

    # Parse metadata from JSON file or args
    if args.metadata_file:
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {
            'name': args.name,
            'description': args.description,
            'author': args.author,
            'version': args.version or '1.0.0',
            'category': args.category or 'general',
            'tags': args.tags.split(',') if args.tags else []
        }

    result = marketplace.publish_agent(args.agent_file, metadata)

    if result['success']:
        print(f"✓ {result['message']}")
        print(f"  Agent ID: {result['agent']['id']}")
    else:
        print(f"✗ Error: {result['error']}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Chalice Agent Marketplace CLI"
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for agents')
    search_parser.add_argument('query', nargs='?', help='Search query')
    search_parser.add_argument('-c', '--category', help='Filter by category')
    search_parser.add_argument('-t', '--tags', help='Filter by tags (comma-separated)')
    search_parser.add_argument('-r', '--min-rating', type=float, default=0.0, help='Minimum rating')
    search_parser.add_argument('-s', '--sort', default='downloads',
                              choices=['downloads', 'rating', 'name', 'updated_at'],
                              help='Sort by')
    search_parser.set_defaults(func=cmd_search)

    # Install command
    install_parser = subparsers.add_parser('install', help='Install an agent')
    install_parser.add_argument('agent_id', help='Agent ID to install')
    install_parser.add_argument('-f', '--force', action='store_true', help='Force reinstall')
    install_parser.set_defaults(func=cmd_install)

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall an agent')
    uninstall_parser.add_argument('agent_id', help='Agent ID to uninstall')
    uninstall_parser.set_defaults(func=cmd_uninstall)

    # Info command
    info_parser = subparsers.add_parser('info', help='Show agent information')
    info_parser.add_argument('agent_id', help='Agent ID')
    info_parser.set_defaults(func=cmd_info)

    # Review command
    review_parser = subparsers.add_parser('review', help='Add a review')
    review_parser.add_argument('agent_id', help='Agent ID')
    review_parser.add_argument('user', help='Your username')
    review_parser.add_argument('rating', type=int, choices=range(1, 6), help='Rating (1-5)')
    review_parser.add_argument('comment', help='Review comment')
    review_parser.set_defaults(func=cmd_review)

    # List command
    list_parser = subparsers.add_parser('list', help='List installed agents or categories')
    list_parser.add_argument('--categories', action='store_true', help='List categories')
    list_parser.set_defaults(func=cmd_list)

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish an agent')
    publish_parser.add_argument('agent_file', help='Path to agent markdown file')
    publish_parser.add_argument('-m', '--metadata-file', help='Path to metadata JSON file')
    publish_parser.add_argument('-n', '--name', help='Agent name')
    publish_parser.add_argument('-d', '--description', help='Agent description')
    publish_parser.add_argument('-a', '--author', help='Author name')
    publish_parser.add_argument('-v', '--version', help='Version')
    publish_parser.add_argument('-c', '--category', help='Category')
    publish_parser.add_argument('-t', '--tags', help='Tags (comma-separated)')
    publish_parser.set_defaults(func=cmd_publish)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()
