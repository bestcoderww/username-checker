import asyncio
import aiohttp
import sys
import time
import re
from socialscan.util import sync_execute_queries
from socialscan.platforms import Platforms

AVAILABLE = "Available"
TAKEN = "Taken"
ERROR = "Error"
INVALID = "Invalid Format"
TIMEOUT_SECONDS = 8
USER_AGENT = 'ben-username-checker/1.9 (python/aiohttp)'

async def check_github(session, username):
    url = f"https://github.com/{username}"
    headers = {'user-agent': USER_AGENT}
    if not re.match(r'^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$', username):
        return INVALID
    try:
        async with session.head(url, timeout=TIMEOUT_SECONDS, allow_redirects=False, headers=headers) as response:
            if response.status == 404:
                return AVAILABLE
            return TAKEN
    except asyncio.TimeoutError:
        return f"{ERROR} (timeout)"
    except aiohttp.ClientError as e:
        return f"{ERROR} (network: {type(e).__name__})"
    except Exception as e:
        return f"{ERROR} (unknown: {type(e).__name__})"

async def check_youtube(session, username):
    url = f"https://www.youtube.com/@{username}"
    headers = {'user-agent': USER_AGENT}
    if not re.match(r'^[a-zA-Z0-9._]{3,30}$', username) or '..' in username:
        return INVALID
    try:
        async with session.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True, headers=headers) as response:
            final_url = str(response.url)
            if response.status == 404:
                return AVAILABLE
            elif response.status == 200 and f"@{username.lower()}" in final_url.lower():
                return TAKEN
            else:
                return AVAILABLE
    except asyncio.TimeoutError:
        return f"{ERROR} (timeout)"
    except aiohttp.ClientError as e:
        return f"{ERROR} (network: {type(e).__name__})"
    except Exception as e:
        return f"{ERROR} (unknown: {type(e).__name__})"

async def check_telegram(session, username):
    url = f"https://t.me/{username}"
    headers = {'user-agent': USER_AGENT}
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{3,31}$', username):
        return INVALID
    try:
        async with session.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True, headers=headers) as response:
            if response.status == 404:
                return AVAILABLE
            elif response.status == 200:
                html_content = await response.text()
                if '<div class="tgme_page_photo">' not in html_content:
                    return AVAILABLE
                else:
                    return TAKEN
            else:
                return f"{ERROR} (status {response.status})"
    except asyncio.TimeoutError:
        return f"{ERROR} (timeout)"
    except aiohttp.ClientError as e:
        return f"{ERROR} (network: {type(e).__name__})"
    except Exception as e:
        return f"{ERROR} (unknown: {type(e).__name__})"

async def check_snapchat(session, username):
    url = f"https://www.snapchat.com/add/{username}"
    headers = {'user-agent': USER_AGENT}
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]{1,13}[a-zA-Z0-9]$', username) or '__' in username or '--' in username or '._' in username or '_.' in username:
        return INVALID
    try:
        async with session.get(url, timeout=TIMEOUT_SECONDS, allow_redirects=True, headers=headers) as response:
            final_url = str(response.url).lower()
            if response.status == 404:
                return AVAILABLE
            elif response.status == 200 and final_url.rstrip('/').endswith(f"/add/{username.lower()}"):
                return TAKEN
            elif response.status == 200 and not final_url.rstrip('/').endswith(f"/add/{username.lower()}"):
                return AVAILABLE
            else:
                return AVAILABLE
    except asyncio.TimeoutError:
        return f"{ERROR} (timeout)"
    except aiohttp.ClientError as e:
        return f"{ERROR} (network: {type(e).__name__})"
    except Exception as e:
        return f"{ERROR} (unknown: {type(e).__name__})"

SOCIALSCAN_PLATFORMS = {
    "twitter": Platforms.TWITTER,
    "instagram": Platforms.INSTAGRAM,
    "reddit": Platforms.REDDIT,
}

CUSTOM_ASYNC_CHECKS = {
    "github": check_github,
    "youtube": check_youtube,
    "telegram": check_telegram,
    "snapchat": check_snapchat,
}

async def run_custom_checks(usernames_to_check):
    custom_platform_tasks = []
    results = {user: {} for user in usernames_to_check}
    headers = {'user-agent': USER_AGENT}
    async with aiohttp.ClientSession(headers=headers) as session:
        platforms_being_checked = list(CUSTOM_ASYNC_CHECKS.keys())
        print(f"\nrunning {len(platforms_being_checked) * len(usernames_to_check)} custom checks ({', '.join(platforms_being_checked)})...")
        start_time = time.monotonic()
        for platform_name, check_function in CUSTOM_ASYNC_CHECKS.items():
            for user in usernames_to_check:
                task = asyncio.create_task(check_function(session, user), name=f"{platform_name}:{user}")
                custom_platform_tasks.append(task)
        if custom_platform_tasks:
            gathered_results = await asyncio.gather(*custom_platform_tasks, return_exceptions=True)
            duration = time.monotonic() - start_time
            print(f"custom checks done in {duration:.2f} sec")
            for i, result_or_exc in enumerate(gathered_results):
                task = custom_platform_tasks[i]
                platform_name, username = task.get_name().split(":", 1)
                if isinstance(result_or_exc, Exception):
                    results[username][platform_name] = f"{ERROR} (task fail: {type(result_or_exc).__name__})"
                else:
                    results[username][platform_name] = result_or_exc
    return results

def run_socialscan_checks(usernames_to_check):
    results = {user: {} for user in usernames_to_check}
    platforms_enum = list(SOCIALSCAN_PLATFORMS.values())
    platform_name_map = {str(p).lower(): p_name for p_name, p in SOCIALSCAN_PLATFORMS.items()}
    if not platforms_enum:
        print("\nno socialscan platforms configured.")
        return results
    print(f"\nrunning socialscan checks for {', '.join(SOCIALSCAN_PLATFORMS.keys())}...")
    start_time = time.monotonic()
    try:
        socialscan_results_list = sync_execute_queries(usernames_to_check, platforms_enum)
        duration = time.monotonic() - start_time
        print(f"socialscan checks done in {duration:.2f} sec")
    except Exception as e:
        print(f"\nerror during socialscan: {type(e).__name__} - {e}", file=sys.stderr)
        for user in usernames_to_check:
            for platform_name in SOCIALSCAN_PLATFORMS.keys():
                results[user][platform_name] = f"{ERROR} (sfailed: {type(e).__name__})"
        return results
    processed_users = set()
    for res in socialscan_results_list:
        status = AVAILABLE if res.available else TAKEN if res.available is False else f"{ERROR} ({res.message})"
        platform_enum_str = str(res.platform).lower()
        platform_name = platform_name_map.get(platform_enum_str, platform_enum_str)
        results[res.query][platform_name] = status
        processed_users.add(res.query)
    for user in usernames_to_check:
        for platform_name in SOCIALSCAN_PLATFORMS.keys():
            if platform_name not in results[user]:
                results[user][platform_name] = f"{ERROR} (no result)"
    return results

if __name__ == "__main__":
    print("""
┌───────────────────────────────────────┐
│        ico's username checker         │
└───────────────────────────────────────┘
""")
    checked_platforms = sorted(list(SOCIALSCAN_PLATFORMS.keys()) + list(CUSTOM_ASYNC_CHECKS.keys()))
    print(f"checks: {', '.join(p for p in checked_platforms)}")

    try:
        raw_input_str = input("enter usernames (comma-separated): ")
    except EOFError:
        print("\nno input received. exiting.", file=sys.stderr)
        sys.exit(1)

    usernames = [u.strip().lower() for u in raw_input_str.split(",") if u.strip()]

    if not usernames:
        print("no valid usernames entered.")
    else:
        print(f"\nchecking {len(usernames)} username(s): {', '.join(usernames)}")
        combined_results = {user: {} for user in usernames}
        all_platforms = sorted(list(SOCIALSCAN_PLATFORMS.keys()) + list(CUSTOM_ASYNC_CHECKS.keys()))
        try:
            socialscan_check_results = run_socialscan_checks(usernames)
            for user, platform_data in socialscan_check_results.items():
                combined_results[user].update(platform_data)

            custom_check_results = asyncio.run(run_custom_checks(usernames))
            for user, platform_data in custom_check_results.items():
                combined_results[user].update(platform_data)

            print("\n🔍 username availability results:\n")
            for user in sorted(usernames):
                print(f"— {user}")
                for platform in sorted(combined_results[user].keys()):
                    status = combined_results[user][platform]
                    prefix = "✅" if status == AVAILABLE else "❌" if status == TAKEN else "❓" if status == INVALID else "⚠️"
                    print(f"   {platform:<10}: {prefix} {status}")
                print()

        except KeyboardInterrupt:
            print("\n\ncancelled by user.", file=sys.stderr)
        except Exception as e:
            print(f"\nunexpected error: {type(e).__name__} - {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
