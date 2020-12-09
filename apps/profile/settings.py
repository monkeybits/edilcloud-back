# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

PROFILE_PROFILE_LANGUAGE_CHOICES = (
    ('it', _('italian'),),
    ('en', _('english'),),
)

PROFILE_PROFILE_ROLE_CHOICES = (
    (settings.OWNER, _('owner'),),
    (settings.DELEGATE, _('delegate'),),
    (settings.LEVEL_1, _('level 1'),),
    (settings.LEVEL_2, _('level 2'),),
)

PROFILE_PROFILE_INVITATION_STATUS_PENDING = -1
PROFILE_PROFILE_INVITATION_STATUS_APPROVED = 1
PROFILE_PROFILE_INVITATION_STATUS_DENIED = 0

PROFILE_PROFILE_NO_REPLY_EMAIL = settings.DEFAULT_FROM_EMAIL

MAX_COMPANIES_PER_USER = 10

PROFILE_PREFERENCE_NOTIFICATION_DEFAULT = {
    "email": {
        "status": False,
        "typology": [
            {
                "name": "company",
                "status": False
            },
            {
                "name": "project",
                "status": False
            },
            {
                "name": "task",
                "status": False
            },
            {
                "name": "activity",
                "status": False
            },
            {
                "name": "post",
                "status": False
            },
            {
                "name": "comment",
                "status": False
            },
            {
                "name": "team",
                "status": False
            },
            {
                "name": "offer",
                "status": False
            },
            {
                "name": "bom",
                "status": False
            },
            {
                "name": "profile",
                "status": False
            },
            {
                "name": "partnership",
                "status": False
            },
            {
                "name": "favourite",
                "status": False
            }
        ]
    },
    "bell": {
        "status": True,
        "typology": [
            {
                "name": "company",
                "status": True
            },
            {
                "name": "project",
                "status": True
            },
            {
                "name": "task",
                "status": True
            },
            {
                "name": "activity",
                "status": True
            },
            {
                "name": "team",
                "status": True
            },
            {
                "name": "offer",
                "status": True
            },
            {
                "name": "bom",
                "status": True
            },
            {
                "name": "profile",
                "status": True
            },
            {
                "name": "partnership",
                "status": True
            },
            {
                "name": "favourite",
                "status": True
            }
        ]
    }
}

PROFILE_PREFERENCE_INFO_DEFAULT = {
    "results": {
        "impostazioni": {
            "title": "impostazioni",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "osservatorio": {
            "title": "osservatorio",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "dashboard": {
            "title": "dashboard",
            "description": "",
            "closed": {},
            "hidden": {
                "media-list": {
                    "boxTitle": "Media list"
                },
                "document-list": {
                    "boxTitle": "Document list"
                },
                "staff-list": {
                    "boxTitle": "Staff list"
                },
                "company-info": {
                    "boxTitle": "company info"
                },
                "staff-gantt": {
                    "boxTitle": "Staff Gantt"
                },
                "internal-project-list": {
                    "boxTitle": "Internal Project list"
                },
                "message-list": {
                    "boxTitle": "Message list"
                }
            },
            "opened": {}
        },
        "marketplace": {
            "title": "marketplace",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {},
            "productCategories": []
        },
        "organico": {
            "title": "organico",
            "description": "",
            "closed": {},
            "hidden": {
                "staff-request-list": {
                    "boxTitle": "Staff Request List"
                },
                "staff-refuse-list": {
                    "boxTitle": "Staff Refuse List"
                },
                "staff-waiting-list": {
                    "boxTitle": "Staff Waiting List"
                },
                "staff-approve-list": {
                    "boxTitle": "Staff Approve List"
                }
            },
            "opened": {}
        },
        "notifiche": {
            "title": "notifiche",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "notification": {
            "title": "notification",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "progetti": {
            "title": "progetti",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "project": {
            "title": "project",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "cronoprogramma": {
            "title": "cronoprogramma",
            "description": "",
            "closed": {},
            "hidden": {
                "staff-gantt": {
                    "boxTitle": "Staff Gantt"
                },
                "project-gantt": {
                    "boxTitle": "Project Gantt"
                },
                "company-gantt": {
                    "boxTitle": "Company Gantt"
                },
                "activity-gantt": {
                    "boxTitle": "Activity Gantt"
                }
            },
            "opened": {}
        },
        "preventivi": {
            "title": "preventivi",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "showroom": {
            "title": "showroom",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "comunica": {
            "title": "comunica",
            "description": "",
            "closed": {},
            "hidden": {},
            "opened": {}
        },
        "imprese": {
            "title": "imprese",
            "description": "",
            "closed": {},
            "hidden": {
                "waiting-companies-list": {
                    "boxTitle": "Waiting Companies List"
                },
                "follower-companies-list": {
                    "boxTitle": "Follower Companies List"
                },
                "companies-list": {
                    "boxTitle": "Companies List"
                },
                "partership-companies-list": {
                    "boxTitle": "Partnership Companies List"
                },
                "received-companies-list": {
                    "boxTitle": "Received Companies List"
                }
            },
            "opened": {}
        }
    }
}
