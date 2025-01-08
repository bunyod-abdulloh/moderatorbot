from loader import dp
from .admins import AdminFilter
from .group_chat import IsGroup, IsGroupAdminOrOwner, IsNewChatMember
from .private_chat import IsPrivate

if __name__ == "filters":
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsGroupAdminOrOwner)
    dp.filters_factory.bind(IsNewChatMember)
