#!/usr/bin/env python3
"""
CLI tool for managing redirects on the Node.js redirector server.
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import Optional


def make_request(method: str, url: str, data: Optional[str] = None) -> dict:
    """Make HTTP request and return parsed JSON response."""
    req = urllib.request.Request(url, data=data.encode() if data else None, method=method)
    # Only add Content-Type for requests with data
    if data:
        req.add_header('Content-Type', 'application/json')
    
    # Create opener that doesn't follow redirects
    class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None  # Don't follow redirects
    
    opener = urllib.request.build_opener(NoRedirectHandler)
    opener.addheaders = []
    # Set User-Agent to match curl
    req.add_header('User-Agent', 'curl/7.68.0')
    
    try:
        with opener.open(req) as response:
            response_data = response.read().decode('utf-8')
            try:
                body = json.loads(response_data) if response_data else {}
            except json.JSONDecodeError:
                body = {'raw_response': response_data}
            return {
                'status_code': response.status,
                'headers': dict(response.headers),
                'body': body
            }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.readable() else ''
        try:
            body = json.loads(error_body) if error_body else {'error': str(e)}
        except json.JSONDecodeError:
            body = {'error': str(e), 'raw_response': error_body}
        return {
            'status_code': e.code,
            'headers': dict(e.headers),
            'body': body
        }
    except Exception as e:
        return {
            'status_code': 0,
            'headers': {},
            'body': {'error': str(e)}
        }


def create_exact_redirect(server_url: str, path: str, destination: str) -> None:
    """Create an exact redirect mapping."""
    url = f"{server_url}{path}?to={urllib.parse.quote(destination)}"
    response = make_request('PUT', url)
    
    if response['status_code'] == 201:
        print(f"✓ Created exact redirect: {path} → {destination}")
    else:
        print(f"✗ Failed to create redirect: {response['body']}", file=sys.stderr)
        sys.exit(1)


def create_pattern_redirect(server_url: str, path: str, destination: str) -> None:
    """Create a pattern redirect mapping."""
    url = f"{server_url}{path}?topattern={urllib.parse.quote(destination)}"
    response = make_request('PUT', url)
    
    if response['status_code'] == 201:
        print(f"✓ Created pattern redirect: {path} → {destination}/*")
    else:
        print(f"✗ Failed to create pattern redirect: {response['body']}", file=sys.stderr)
        sys.exit(1)


def create_proxy(server_url: str, host: str, destination: str) -> None:
    """Create a proxy mapping for a host."""
    url = f"{server_url}/?host={urllib.parse.quote(host)}&proxy={urllib.parse.quote(destination)}"
    response = make_request('PUT', url)

    if response['status_code'] == 201:
        print(f"✓ Created proxy: {host} → {destination}")
    else:
        print(f"✗ Failed to create proxy: {response['body']}", file=sys.stderr)
        sys.exit(1)


def test_redirect(server_url: str, path: str) -> None:
    """Test a redirect by following it."""
    url = f"{server_url}{path}"
    response = make_request('GET', url)

    if response['status_code'] == 302:
        # HTTP headers are case-insensitive, so check both cases
        headers = response['headers']
        location = headers.get('location') or headers.get('Location', 'Unknown')
        print(f"✓ Redirect found: {path} → {location}")
    elif response['status_code'] == 404:
        print(f"✗ No redirect found for: {path}")
    else:
        print(f"✗ Unexpected response: {response['status_code']} {response['body']}")


def main():
    parser = argparse.ArgumentParser(
        prog='redirector-cli',
        description="CLI tool for managing redirects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s exact /short https://example.com/long-url
  %(prog)s pattern /docs https://docs.example.com
  %(prog)s proxy api.example.com https://backend.example.com
  %(prog)s test /short
        """
    )
    
    parser.add_argument(
        '--server', '-s',
        default='http://127.0.0.1:80',
        help='Redirector server URL (default: http://127.0.0.1:80)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Exact redirect command
    exact_parser = subparsers.add_parser('exact', help='Create exact redirect')
    exact_parser.add_argument('path', help='Source path (e.g., /short)')
    exact_parser.add_argument('destination', help='Destination URL')
    
    # Pattern redirect command
    pattern_parser = subparsers.add_parser('pattern', help='Create pattern redirect')
    pattern_parser.add_argument('path', help='Base path (e.g., /docs)')
    pattern_parser.add_argument('destination', help='Destination base URL')

    # Proxy command
    proxy_parser = subparsers.add_parser('proxy', help='Create host-based proxy')
    proxy_parser.add_argument('host', help='Hostname to proxy (e.g., api.example.com)')
    proxy_parser.add_argument('destination', help='Destination URL to proxy to')

    # Test redirect command
    test_parser = subparsers.add_parser('test', help='Test a redirect')
    test_parser.add_argument('path', help='Path to test')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Ensure server URL doesn't end with slash
    server_url = args.server.rstrip('/')
    
    if args.command == 'exact':
        create_exact_redirect(server_url, args.path, args.destination)
    elif args.command == 'pattern':
        create_pattern_redirect(server_url, args.path, args.destination)
    elif args.command == 'proxy':
        create_proxy(server_url, args.host, args.destination)
    elif args.command == 'test':
        test_redirect(server_url, args.path)


if __name__ == '__main__':
    main()
