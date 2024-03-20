from .models import User, LocalSession, Ad


def set_user(user_id, is_admin=False):
    try:
        with LocalSession() as session:
            instance = User(id=user_id, is_admin=is_admin)
            session.add(instance)
            session.commit()
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def get_user(user_id):
    try:
        with LocalSession() as session:
            user = session.query(User).get(user_id)
            if user:
                return user.id, user.is_admin
            else:
                return None, None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None, None


def add_admin(user_id):
    try:
        with LocalSession() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.is_admin = True
                session.commit()
                print(f"Пользователь с ID {user_id} был добавлен в список администраторов.")
            else:
                print(f"Пользователь с ID {user_id} не найден в базе данных.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def del_admin(user_id):
    try:
        with LocalSession() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.is_admin = False
                session.commit()
                print(f"Пользователь с ID {user_id} был удален из списка администраторов.")
            else:
                print(f"Пользователь с ID {user_id} не найден в базе данных.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")



def set_ad(title, area, price, room, square, tenant_span, url, images, city):
    with LocalSession() as session:
        instance = session.query(Ad).filter_by(url=url).first()

        if instance:
            print('Объявление уже спаршено')
            instance.title = title
            instance.area = area
            instance.price = price
            instance.room = room
            instance.square = square
            instance.tenant_span = tenant_span
            instance.images = ','.join(images) if images else None
            instance.city = city
        else:
            instance = Ad(title=title, area=area, price=price, room=room, square=square, city=city,
                          tenant_span=tenant_span, url=url, images=','.join(images))
            session.add(instance)
        session.commit()


async def get_all_ads():
    with LocalSession() as session:
        ads = session.query(Ad).all()
        session.close()
        return ads
