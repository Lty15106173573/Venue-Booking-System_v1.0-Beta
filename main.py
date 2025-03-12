#VBS场地预约系统_v1.0-Beta Venue Booking System_v1.0-Beta
#本程序由bilibili @欧拉公社EulerCommune(UID:1646259674) 及 @cooperrrrrrr0917(UID:3546704301263608) 共同编写 This program is co-written by bilibili @欧拉公社EulerCommune (UID:1646259674) and @cooperrrrrrr0917(UID:3546704301263608)


import os
import json
import datetime
import csv
from time import sleep
from collections import defaultdict

# 颜色配置
COLOR = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}

# 文件配置
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
VENUES_FILE = os.path.join(DATA_DIR, "venues.json")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
LOG_FILE = os.path.join(DATA_DIR, "activity.log")

def init_system():
    """初始化系统环境"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    default_files = {
        USERS_FILE: [
            {
                "username": "admin",
                "password": "admin",
                "is_admin": True
            }
        ],
        VENUES_FILE: [
            {"id": 1, "name": "禅意茶室", "capacity": 10, "description": "静心品茗空间"},
            {"id": 2, "name": "竹林会议室", "capacity": 20, "description": "自然风格会议空间"}
        ],
        BOOKINGS_FILE: [],
        LOG_FILE: ""
    }
    
    for file_path, default_content in default_files.items():
        if not os.path.exists(file_path):
            if isinstance(default_content, list):
                save_data(default_content, file_path)
            else:
                with open(file_path, 'w') as f:
                    f.write(default_content)

def log_activity(username, action):
    """记录用户活动日志"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {username}: {action}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)

def clear_screen():
    """清屏函数"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """打印带颜色的标题"""
    clear_screen()
    border = COLOR['CYAN'] + "=" * 50 + COLOR['ENDC']
    print(f"\n{border}")
    print(f"{COLOR['BOLD']}{COLOR['YELLOW']}{title:^50}{COLOR['ENDC']}")
    print(f"{border}\n")

def load_data(filename):
    """加载JSON数据"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data, filename):
    """保存JSON数据"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def login():
    """用户登录"""
    print_header("用户登录")
    username = input(f"{COLOR['BLUE']}用户名: {COLOR['ENDC']}")
    password = input(f"{COLOR['BLUE']}密码: {COLOR['ENDC']}")
    
    users = load_data(USERS_FILE)
    user = next((u for u in users if u['username'] == username), None)
    
    if user and user.get('password') == password:
        print(f"\n{COLOR['GREEN']}登录成功!{COLOR['ENDC']}")
        sleep(1)
        return user
    else:
        print(f"\n{COLOR['RED']}认证失败!{COLOR['ENDC']}")
        sleep(1)
        return None

def register():
    """用户注册"""
    print_header("用户注册")
    username = input(f"{COLOR['BLUE']}用户名: {COLOR['ENDC']}")
    
    if any(u['username'] == username for u in load_data(USERS_FILE)):
        print(f"\n{COLOR['RED']}用户名已存在!{COLOR['ENDC']}")
        sleep(1)
        return
    
    password = input(f"{COLOR['BLUE']}密码: {COLOR['ENDC']}")
    
    new_user = {
        'username': username,
        'password': password,
        'is_admin': False
    }
    
    users = load_data(USERS_FILE)
    users.append(new_user)
    save_data(users, USERS_FILE)
    
    print(f"\n{COLOR['GREEN']}注册成功!{COLOR['ENDC']}")
    log_activity(username, "新用户注册")
    sleep(1)

def show_venues():
    """显示所有场地"""
    venues = load_data(VENUES_FILE)
    print(f"\n{COLOR['CYAN']}{'场地列表':^50}{COLOR['ENDC']}")
    print(f"{COLOR['GREEN']}{'ID':<5}{'名称':<20}{'容量':<10}{'描述'}{COLOR['ENDC']}")
    for venue in venues:
        print(f"{venue['id']:<5}{venue['name']:<20}{venue['capacity']:<10}{venue['description']}")

def get_venue_by_id(venue_id):
    """通过ID获取场地信息"""
    venues = load_data(VENUES_FILE)
    return next((v for v in venues if v['id'] == venue_id), None)

def add_venue(user):
    """添加场地"""
    print_header("添加新场地")
    name = input(f"{COLOR['BLUE']}场地名称: {COLOR['ENDC']}")
    capacity = input(f"{COLOR['BLUE']}场地容量: {COLOR['ENDC']}")
    description = input(f"{COLOR['BLUE']}场地描述: {COLOR['ENDC']}")
    
    venues = load_data(VENUES_FILE)
    new_id = max(v['id'] for v in venues) + 1 if venues else 1
    venues.append({
        'id': new_id,
        'name': name,
        'capacity': capacity,
        'description': description
    })
    
    save_data(venues, VENUES_FILE)
    print(f"\n{COLOR['GREEN']}场地添加成功!{COLOR['ENDC']}")
    log_activity(user['username'], f"添加场地: {name}")
    sleep(1)

def time_conflict(new_start, new_end, existing_start, existing_end):
    """检查时间冲突"""
    return (new_start < existing_end) and (new_end > existing_start)

def book_venue(user):
    """场地预约"""
    print_header("场地预约")
    show_venues()
    
    try:
        venue_id = int(input(f"\n{COLOR['BLUE']}选择场地ID: {COLOR['ENDC']}"))
        start_str = input(f"{COLOR['BLUE']}开始时间(YYYY-MM-DD HH:MM): {COLOR['ENDC']}")
        end_str = input(f"{COLOR['BLUE']}结束时间(YYYY-MM-DD HH:MM): {COLOR['ENDC']}")
        
        start_time = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M")
        end_time = datetime.datetime.strptime(end_str, "%Y-%m-%d %H:%M")
        
        if start_time >= end_time:
            raise ValueError("结束时间必须晚于开始时间")
    except Exception as e:
        print(f"\n{COLOR['RED']}错误: {str(e)}{COLOR['ENDC']}")
        sleep(2)
        return
    
    bookings = load_data(BOOKINGS_FILE)
    for booking in bookings:
        if booking['venue_id'] == venue_id:
            existing_start = datetime.datetime.strptime(booking['start_time'], "%Y-%m-%d %H:%M")
            existing_end = datetime.datetime.strptime(booking['end_time'], "%Y-%m-%d %H:%M")
            if time_conflict(start_time, end_time, existing_start, existing_end):
                print(f"\n{COLOR['RED']}时间冲突!{COLOR['ENDC']}")
                sleep(2)
                return
    
    new_booking = {
        'id': len(bookings) + 1,
        'user': user['username'],
        'venue_id': venue_id,
        'start_time': start_str,
        'end_time': end_str
    }
    bookings.append(new_booking)
    save_data(bookings, BOOKINGS_FILE)
    
    print(f"\n{COLOR['GREEN']}预约成功!{COLOR['ENDC']}")
    log_activity(user['username'], f"预约场地ID:{venue_id}")
    sleep(1)

def change_password(user):
    """修改密码"""
    print_header("修改密码")
    current_pass = input(f"{COLOR['BLUE']}当前密码: {COLOR['ENDC']}")
    
    if user.get('password') != current_pass:
        print(f"{COLOR['RED']}密码错误!{COLOR['ENDC']}")
        sleep(1)
        return
    
    new_pass = input(f"{COLOR['BLUE']}新密码: {COLOR['ENDC']}")
    confirm_pass = input(f"{COLOR['BLUE']}确认新密码: {COLOR['ENDC']}")
    
    if new_pass != confirm_pass:
        print(f"{COLOR['RED']}两次输入不一致!{COLOR['ENDC']}")
        sleep(1)
        return
    
    users = load_data(USERS_FILE)
    for u in users:
        if u['username'] == user['username']:
            u['password'] = new_pass
    save_data(users, USERS_FILE)
    print(f"{COLOR['GREEN']}密码修改成功!{COLOR['ENDC']}")
    log_activity(user['username'], "修改密码")
    sleep(1)

def my_bookings(user):
    """查看我的预约"""
    bookings = load_data(BOOKINGS_FILE)
    user_bookings = [b for b in bookings if b['user'] == user['username']]
    
    print(f"\n{COLOR['CYAN']}{'我的预约':^50}{COLOR['ENDC']}")
    print(f"{COLOR['GREEN']}{'ID':<5}{'场地':<15}{'开始时间':<20}{'结束时间'}{COLOR['ENDC']}")
    for b in user_bookings:
        venue = get_venue_by_id(b['venue_id'])
        print(f"{b['id']:<5}{venue['name'] if venue else '未知场地':<15}{b['start_time']:<20}{b['end_time']}")
    input(f"\n{COLOR['YELLOW']}按回车返回...{COLOR['ENDC']}")

def cancel_booking(user):
    """取消预约"""
    my_bookings(user)
    try:
        booking_id = int(input(f"\n{COLOR['BLUE']}输入要取消的预约ID: {COLOR['ENDC']}"))
    except ValueError:
        print(f"{COLOR['RED']}无效的ID格式!{COLOR['ENDC']}")
        sleep(1)
        return
    
    bookings = load_data(BOOKINGS_FILE)
    original_count = len(bookings)
    bookings = [b for b in bookings if not (b['id'] == booking_id and b['user'] == user['username'])]
    
    if len(bookings) == original_count:
        print(f"{COLOR['RED']}未找到预约记录!{COLOR['ENDC']}")
    else:
        save_data(bookings, BOOKINGS_FILE)
        print(f"{COLOR['GREEN']}预约取消成功!{COLOR['ENDC']}")
        log_activity(user['username'], f"取消预约ID:{booking_id}")
    sleep(1)

def generate_report():
    """生成统计报表"""
    print_header("系统统计")
    venues = load_data(VENUES_FILE)
    bookings = load_data(BOOKINGS_FILE)
    
    venue_stats = defaultdict(int)
    for b in bookings:
        venue_stats[b['venue_id']] += 1
    
    print(f"{COLOR['CYAN']}场地使用次数统计:{COLOR['ENDC']}")
    for vid, count in venue_stats.items():
        venue = get_venue_by_id(vid)
        print(f"{venue['name'] if venue else '未知场地'}: {count}次")
    
    user_stats = defaultdict(int)
    for b in bookings:
        user_stats[b['user']] += 1
    
    print(f"\n{COLOR['CYAN']}用户活跃度统计:{COLOR['ENDC']}")
    for user, count in user_stats.items():
        print(f"{user}: {count}次")
    
    input(f"\n{COLOR['YELLOW']}按回车返回...{COLOR['ENDC']}")

def export_data():
    """导出数据为CSV"""
    print_header("数据导出")
    print(f"{COLOR['GREEN']}1. 导出用户数据\n2. 导出场地数据\n3. 导出预约数据{COLOR['ENDC']}")
    choice = input(f"{COLOR['YELLOW']}> 请选择要导出的数据类型: {COLOR['ENDC']}")
    
    filename_map = {
        '1': ('users.csv', load_data(USERS_FILE)),
        '2': ('venues.csv', load_data(VENUES_FILE)),
        '3': ('bookings.csv', load_data(BOOKINGS_FILE))
    }
    
    if choice not in filename_map:
        print(f"{COLOR['RED']}无效选择!{COLOR['ENDC']}")
        sleep(1)
        return
    
    filename, data = filename_map[choice]
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    print(f"{COLOR['GREEN']}数据已导出到 {filename}{COLOR['ENDC']}")
    log_activity("System", f"导出数据: {filename}")
    sleep(1)

def list_users():
    """列出所有用户"""
    users = load_data(USERS_FILE)
    print(f"\n{COLOR['CYAN']}{'用户列表':^50}{COLOR['ENDC']}")
    print(f"{COLOR['GREEN']}{'用户名':<20}{'管理员权限'}{COLOR['ENDC']}")
    for u in users:
        admin_status = '是' if u.get('is_admin', False) else '否'
        print(f"{u['username']:<20}{admin_status}")

def delete_user(admin_user):
    """删除用户"""
    list_users()
    username = input(f"\n{COLOR['BLUE']}输入要删除的用户名: {COLOR['ENDC']}")
    if username == admin_user['username']:
        print(f"{COLOR['RED']}不能删除当前管理员账户!{COLOR['ENDC']}")
        sleep(1)
        return
    
    users = load_data(USERS_FILE)
    original_count = len(users)
    users = [u for u in users if u['username'] != username]
    
    if len(users) == original_count:
        print(f"{COLOR['RED']}用户不存在!{COLOR['ENDC']}")
    else:
        save_data(users, USERS_FILE)
        print(f"{COLOR['GREEN']}用户删除成功!{COLOR['ENDC']}")
        log_activity(admin_user['username'], f"删除用户: {username}")
    sleep(1)

def toggle_admin(admin_user):
    """切换用户管理员权限"""
    list_users()
    username = input(f"\n{COLOR['BLUE']}输入要修改权限的用户名: {COLOR['ENDC']}")
    if username == admin_user['username']:
        print(f"{COLOR['RED']}不能修改当前管理员权限!{COLOR['ENDC']}")
        sleep(1)
        return
    
    users = load_data(USERS_FILE)
    user = next((u for u in users if u['username'] == username), None)
    if not user:
        print(f"{COLOR['RED']}用户不存在!{COLOR['ENDC']}")
        sleep(1)
        return
    
    user['is_admin'] = not user.get('is_admin', False)
    save_data(users, USERS_FILE)
    action = "授予管理员权限" if user['is_admin'] else "撤销管理员权限"
    print(f"{COLOR['GREEN']}{action}成功!{COLOR['ENDC']}")
    log_activity(admin_user['username'], f"{action}用户: {username}")
    sleep(1)

def manage_users(user):
    """用户管理菜单"""
    while True:
        print_header("用户管理")
        print(f"{COLOR['GREEN']}1. 查看用户列表\n2. 删除用户\n3. 修改权限\n4. 返回上级{COLOR['ENDC']}")
        choice = input(f"{COLOR['YELLOW']}> 请选择操作: {COLOR['ENDC']}")
        
        if choice == '1':
            list_users()
            input(f"\n{COLOR['YELLOW']}按回车返回...{COLOR['ENDC']}")
        elif choice == '2':
            delete_user(user)
        elif choice == '3':
            toggle_admin(user)
        elif choice == '4':
            break
        else:
            print(f"{COLOR['RED']}无效选择!{COLOR['ENDC']}")
            sleep(1)

def delete_venue(user):
    """删除场地"""
    show_venues()
    try:
        venue_id = int(input(f"\n{COLOR['BLUE']}输入要删除的场地ID: {COLOR['ENDC']}"))
    except ValueError:
        print(f"{COLOR['RED']}无效的ID格式!{COLOR['ENDC']}")
        sleep(1)
        return
    
    venues = load_data(VENUES_FILE)
    bookings = load_data(BOOKINGS_FILE)
    
    if any(b['venue_id'] == venue_id for b in bookings):
        print(f"{COLOR['RED']}该场地存在历史预约，无法删除!{COLOR['ENDC']}")
        sleep(2)
        return
    
    venues = [v for v in venues if v['id'] != venue_id]
    save_data(venues, VENUES_FILE)
    print(f"{COLOR['GREEN']}场地删除成功!{COLOR['ENDC']}")
    log_activity(user['username'], f"删除场地ID:{venue_id}")
    sleep(1)

def modify_venue(user):
    """修改场地信息"""
    show_venues()
    try:
        venue_id = int(input(f"\n{COLOR['BLUE']}输入要修改的场地ID: {COLOR['ENDC']}"))
    except ValueError:
        print(f"{COLOR['RED']}无效的ID格式!{COLOR['ENDC']}")
        sleep(1)
        return

    venues = load_data(VENUES_FILE)
    venue = next((v for v in venues if v['id'] == venue_id), None)
    
    if not venue:
        print(f"{COLOR['RED']}未找到该场地!{COLOR['ENDC']}")
        sleep(1)
        return
    
    print(f"\n{COLOR['CYAN']}当前信息：")
    print(f"名称: {venue['name']}")
    print(f"容量: {venue['capacity']}")
    print(f"描述: {venue['description']}{COLOR['ENDC']}")
    
    new_name = input(f"\n{COLOR['BLUE']}新名称（留空保持不变）: {COLOR['ENDC']}") or venue['name']
    new_capacity = input(f"{COLOR['BLUE']}新容量（留空保持不变）: {COLOR['ENDC']}") or venue['capacity']
    new_desc = input(f"{COLOR['BLUE']}新描述（留空保持不变）: {COLOR['ENDC']}") or venue['description']
    
    venue['name'] = new_name
    venue['capacity'] = new_capacity
    venue['description'] = new_desc
    
    save_data(venues, VENUES_FILE)
    print(f"{COLOR['GREEN']}场地信息更新成功!{COLOR['ENDC']}")
    log_activity(user['username'], f"修改场地ID:{venue_id}")
    sleep(1)

def manage_venues(user):
    """场地管理菜单"""
    while True:
        print_header("场地管理")
        print(f"{COLOR['GREEN']}1. 添加场地\n2. 删除场地\n3. 修改场地\n4. 返回上级{COLOR['ENDC']}")
        choice = input(f"{COLOR['YELLOW']}> 请选择操作: {COLOR['ENDC']}")
        
        if choice == '1':
            add_venue(user)
        elif choice == '2':
            delete_venue(user)
        elif choice == '3':
            modify_venue(user)
        elif choice == '4':
            break
        else:
            print(f"{COLOR['RED']}无效选择!{COLOR['ENDC']}")
            sleep(1)

def admin_menu(user):
    """管理员专属菜单"""
    while True:
        print_header("管理控制台")
        print(f"{COLOR['GREEN']}1. 场地管理\n2. 用户管理\n3. 系统统计\n4. 导出数据\n5. 返回上级{COLOR['ENDC']}")
        choice = input(f"{COLOR['YELLOW']}> 请选择操作: {COLOR['ENDC']}")
        
        if choice == '1':
            manage_venues(user)
        elif choice == '2':
            manage_users(user)
        elif choice == '3':
            generate_report()
        elif choice == '4':
            export_data()
        elif choice == '5':
            break
        else:
            print(f"{COLOR['RED']}无效选择!{COLOR['ENDC']}")
            sleep(1)

def main():
    """主程序入口"""
    init_system()
    current_user = None
    
    while True:
        print_header("VBS场地预约系统_v1.0-Beta Venue Booking System_v1.0-Beta\nbilibili @欧拉公社EulerCommune @cooperrrrrrr0917")
        
        if not current_user:
            print(f"{COLOR['GREEN']}1. 登录\n2. 注册\n3. 退出{COLOR['ENDC']}")
            choice = input(f"{COLOR['YELLOW']}> 请选择操作: {COLOR['ENDC']}")
            
            if choice == '1':
                current_user = login()
                if current_user:
                    log_activity(current_user['username'], "登录系统")
            elif choice == '2':
                register()
            elif choice == '3':
                print(f"\n{COLOR['CYAN']}感谢使用，再见!{COLOR['ENDC']}")
                break
            else:
                print(f"\n{COLOR['RED']}无效选择!{COLOR['ENDC']}")
                sleep(1)
        else:
            is_admin = current_user.get('is_admin', False)
            
            print(f"{COLOR['GREEN']}欢迎回来，{current_user['username']}{COLOR['ENDC']}")
            print(f"{COLOR['GREEN']}1. 预约场地\n2. 我的预约\n3. 取消预约\n4. 修改密码\n5. 退出登录{COLOR['ENDC']}")
            if is_admin:
                print(f"{COLOR['GREEN']}6. 管理控制台{COLOR['ENDC']}")
            
            choice = input(f"{COLOR['YELLOW']}> 请选择操作: {COLOR['ENDC']}")
            
            if choice == '1':
                book_venue(current_user)
                log_activity(current_user['username'], "新增预约")
            elif choice == '2':
                my_bookings(current_user)
            elif choice == '3':
                cancel_booking(current_user)
            elif choice == '4':
                change_password(current_user)
            elif choice == '5':
                log_activity(current_user['username'], "退出登录")
                current_user = None
            elif choice == '6' and is_admin:
                admin_menu(current_user)
            else:
                print(f"\n{COLOR['RED']}无效选择!{COLOR['ENDC']}")
                sleep(1)

if __name__ == "__main__":
    main()