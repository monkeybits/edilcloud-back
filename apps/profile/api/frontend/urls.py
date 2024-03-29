    # -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.profile.api.frontend.views import (
    generic_views,
    tracker_views,
    user_views,
)
# Todo: some URLS are not listed here. We will add it soon.
app_name = 'profile'

user_urlpatterns = [
    url(
        r'^company/add/$',
        user_views.CompanyAddView.as_view(),
        name='company_add'
    ),
    url(
        r'^profiles/active_list/$',
        user_views.ProfilesActiveListView.as_view(),
        name='profiles_active_list'
    ),
    url(
        r'^my_company/list/$',
        user_views.MyCompanyListView.as_view(),
        name='my_company_list'
    ),
    url(
        r'^my_company/active_list/$',
        user_views.MyCompanyActiveListView.as_view(),
        name='my_company_active_list'
    ),
    url(
        r'^my_company/inactive_list/$',
        user_views.MyCompanyInactiveListView.as_view(),
        name='my_company_inactive_list'
    ),
    url(
        r'^profile/active_list/$',
        user_views.ProfileActiveListView.as_view(),
        name='profile_active_list'
    ),
    url(
        r'^profile/add/$',
        user_views.ProfileAddView.as_view(),
        name='profile_add'
    ),
    url(
        r'^profile/(?P<type>(request|approve|refuse|waiting){1})_list/$',
        user_views.ProfileListView.as_view(),
        name='profile_list'
    ),
    url(
        r'^profile/edit/(?P<pk>\d+)/$',
        user_views.ProfileEditView.as_view(),
        name='profile_edit'
    ),
    url(
        r'^profile/enable/(?P<pk>\d+)/$',
        user_views.ProfileEnableView.as_view(),
        name='profile_profile_enable'
    ),
    url(
        r'^profile/disable/(?P<pk>\d+)/$',
        user_views.ProfileDisableView.as_view(),
        name='profile_profile_disable'
    ),
    url(
        r'^profile/delete/(?P<pk>\d+)/$',
        user_views.ProfileDeleteView.as_view(),
        name='profile_delete'
    ),
    url(
        r'^profile/send_invite/(?P<company_pk>\d+)/$',
        user_views.ProfileSendInviteView.as_view(),
        name='profile_send_invite'
    ),
]

# Todo: Generic views would be fixed,  only after the discussion with the customer (Whistle).
generic_urlpatterns = [
    url(
        r'^company/$',
        generic_views.CompanyListView.as_view(),
        name='company_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/$',
        generic_views.CompanyDetailView.as_view(),
        name='company_detail'
    ),
    url(
        r'^company/(?P<pk>\d+)/photo_list/$',
        generic_views.CompanyPhotoListView.as_view(),
        name='company_photo_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/company_photo_list/public/$',
        generic_views.CompanyPublicPhotoListView.as_view(),
        name='company__public_photo_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/video_list/$',
        generic_views.CompanyVideoListView.as_view(),
        name='company_video_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/company_video_list/public/$',
        generic_views.CompanyPublicVideoListView.as_view(),
        name='company_public_video_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/offer_list/$',
        generic_views.CompanyOfferListView.as_view(),
        name='company_offer_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/active_offer_list/$',
        generic_views.CompanyActiveOfferListView.as_view(),
        name='company_offer_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/partnership/$',
        generic_views.CompanyPartnerShipList.as_view(),
        name='company_partnership_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/certification_list/$',
        generic_views.CompanyCertificationListView.as_view(),
        name='company_certification_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/staff_list/$',
        generic_views.CompanyStaffListView.as_view(),
        name='company_staff_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/public_staff_list/$',
        generic_views.CompanyPublicStaffListView.as_view(),
        name='company_public_staff_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/showroom_staff_list/$',
        generic_views.CompanyShowroomContactListView.as_view(),
        name='company_showroom_contact_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/owner_list/$',
        generic_views.CompanyOwnerListView.as_view(),
        name='company_owner_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/delegate_list/$',
        generic_views.CompanyDelegateListView.as_view(),
        name='company_delegate_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/level1_list/$',
        generic_views.CompanyLevel1ListView.as_view(),
        name='company_level1_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/level2_list/$',
        generic_views.CompanyLevel2ListView.as_view(),
        name='company_level2_list'
    ),
    url(
        r'^profile/(?P<pk>\d+)/$',
        generic_views.ProfileDetailView.as_view(),
        name='profile_detail'
    ),
]

tracker_urlpatterns = [
    url(
        r'^company/list/$',
        tracker_views.CompanyListView.as_view(),
        name='company_list'
    ),
    url(
        r'^profile/accept_invite/(?P<base36>[\w-]+)-(?P<token>[\w-]+)/$',
        tracker_views.TrackerProfileAcceptInviteView.as_view(),
        name='tracker_profile_accept_invite'
    ),
    url(
        r'^profile/refuse_invite/(?P<base36>[\w-]+)-(?P<token>[\w-]+)/$',
        tracker_views.TrackerProfileRefuseInviteView.as_view(),
        name='tracker_profile_refuse_invite'
    ),
    url(
        r'^profile/reaccept_invite/(?P<pk>\d+)/$',
        tracker_views.TrackerProfileReAcceptInviteView.as_view(),
        name='tracker_profile_reaccept_invite'
    ),
    url(
        r'^profile/change_showroom_visibility/(?P<pk>\d+)/$',
        tracker_views.TrackerProfileChangeShowroomVisibilityView.as_view(),
        name='tracker_profile_change_visibility'
    ),
    url(
        r'^profile/change_comunica_visibility/(?P<pk>\d+)/$',
        tracker_views.TrackerProfileChangeComunicaVisibilityView.as_view(),
        name='tracker_profile_change_visibility'
    ),
    url(
        r'^profile/(?P<pk>\d+)/document_list/$',
        tracker_views.TrackerProfileDocumentListView.as_view(),
        name='tracker_profile_document_list'
    ),
    url(
        r'^preference/detail/$',
        tracker_views.TrackerPreferenceDetailView.as_view(),
        name='tracker_preference_detail'
    ),
    url(
        r'^preference/edit/$',
        tracker_views.TrackerPreferenceEditView.as_view(),
        name='tracker_preference_edit'
    ),
    url(
        r'^company/profile_add/$',
        tracker_views.TrackerCompanyProfileAddView.as_view(),
        name='tracker_company_profile_add'
    ),
    url(
        r'^company/invite/profile_add/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyInviteProfileAddView.as_view(),
        name='tracker_invite_company_profile_add'
    ),
    url(
        r'^company/profile_list/$',
        tracker_views.TrackerCompanyProfileListView.as_view(),
        name='tracker_company_profile_list'
    ),
    # TODO: active, phantoms, guests as so on
    url(
        r'^company/profile_detail/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyProfileDetailView.as_view(),
        name='tracker_company_profile_detail'
    ),
    url(
        r'^company/profile_edit/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyProfileEditView.as_view(),
        name='tracker_company_profile_edit'
    ),
    url(
        r'^company/profile_enable/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyProfileEnableView.as_view(),
        name='tracker_company_profile_enable'
    ),
    url(
        r'^company/profile_disable/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyProfileDisableView.as_view(),
        name='tracker_company_profile_disable'
    ),
    # TODO: only for test
    url(
        r'^company/profile_delete/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyProfileDeleteView.as_view(),
        name='tracker_company_profile_delete'
    ),
    url(
        r'^company/follow/$',
        tracker_views.TrackerCompanyFollowView.as_view(),
        name='tracker_company_follow'
    ),
    url(
        r'^company/(?P<company_id>\d+)/unfollow/$',
        tracker_views.TrackerCompanyUnFollowView.as_view(),
        name='tracker_company_unfollow'
    ),
    url(
        r'^company/(?P<pk>\d+)/follower_accept/$',
        tracker_views.TrackerCompanyAcceptFollowView.as_view(),
        name='tracker_company_accept_follow'
    ),
    url(
        r'^company/(?P<pk>\d+)/follower/(?P<company>\d+)/refuse/$',
        tracker_views.TrackerCompanyRefuseFollowView.as_view(),
        name='tracker_company_refuse_follow'
    ),
    # TODO: only for test
    url(
        r'^company/delete/$',
        tracker_views.TrackerCompanyDeleteView.as_view(),
        name='tracker_company_delete'
    ),
    url(
        r'^company/(?P<pk>\d+)/edit/$',
        tracker_views.TrackerCompanyEditView.as_view(),
        name='tracker_company_edit'
    ),
    url(
        r'^company/enable/$',
        tracker_views.TrackerCompanyEnableView.as_view(),
        name='tracker_company_enable'
    ),
    url(
        r'^company/disable/$',
        tracker_views.TrackerCompanyDisableView.as_view(),
        name='tracker_company_disable'
    ),
    url(
        r'^company/detail/$',
        tracker_views.TrackerCompanyDetailView.as_view(),
        name='tracker_company_detail'
    ),
    url(
        r'^company/partnership/(?P<type>(request|approve|refuse|waiting){1})/list/$',
        tracker_views.TrackerCompanyPartnerShipListView.as_view(),
        name='tracker_company_partnership_list'
    ),
    url(
        r'^company/(?P<pk>\d+)/partnership_add/$',
        tracker_views.TrackerCompanyPartnerShipAddView.as_view(),
        name='tracker_company_partnership_add'
    ),
    url(
        r'^company/(?P<pk>\d+)/partnership_accept/$',
        tracker_views.TrackerCompanyPartnerShipAcceptView.as_view(),
        name='tracker_company_partnership_accept'
    ),
    url(
        r'^company/(?P<pk>\d+)/partnership_refuse/$',
        tracker_views.TrackerCompanyPartnerShipRefuseView.as_view(),
        name='tracker_company_partnership_refuse'
    ),
    url(
        r'^company/message_list/(?P<type>(all|last){1})/$',
        tracker_views.TrackerCompanyMessageListView.as_view(),
        name='tracker_company_message_list'
    ),
    url(
        r'^company/document_list/$',
        tracker_views.TrackerCompanyDocumentListView.as_view(),
        name='tracker_company_document_list'
    ),
    url(
        r'^company/company_document_list/$',
        tracker_views.TrackerCompanyCompanyDocumentListView.as_view(),
        name='tracker_company_company_document_list'
    ),
    url(
        r'^company/company_document_list/(?P<type>(private|public){1})/$',
        tracker_views.TrackerCompanyCompanyDocumentListView.as_view(),
        name='tracker_company_company_private_public_document_list'
    ),
    url(
        r'^company/project_document_list/$',
        tracker_views.TrackerCompanyProjectDocumentListView.as_view(),
        name='tracker_company_project_document_list'
    ),
    url(
        r'^company/profile_document_list/$',
        tracker_views.TrackerCompanyProfileDocumentListView.as_view(),
        name='tracker_company_profile_document_list'
    ),
    url(
        r'^company/bom_document_list/$',
        tracker_views.TrackerCompanyBomDocumentListView.as_view(),
        name='tracker_company_bom_document_list'
    ),
    url(
        r'^company/talk_list/$',
        tracker_views.TrackerCompanyTalkListView.as_view(),
        name='tracker_company_talk_list'
    ),
    url(
        r'^company/company_talk_list/$',
        tracker_views.TrackerCompanyCompanyTalkListView.as_view(),
        name='tracker_company_company_talk_list'
    ),
    url(
        r'^company/project_talk_list/$',
        tracker_views.TrackerCompanyProjectTalkListView.as_view(),
        name='tracker_company_project_talk_list'
    ),
    url(
        r'^company/profile_talk_list/$',
        tracker_views.TrackerCompanyProfileTalkListView.as_view(),
        name='tracker_company_profile_talk_list'
    ),
    url(
        r'^company/photo_list/$',
        tracker_views.TrackerCompanyPhotoListView.as_view(),
        name='tracker_company_photo_list'
    ),
    url(
        r'^company/company_photo_list/$',
        tracker_views.TrackerCompanyCompanyPhotoListView.as_view(),
        name='tracker_company_company_photo_list'
    ),
    url(
        r'^company/company_photo_list/(?P<type>(private|public){1})/$',
        tracker_views.TrackerCompanyCompanyPhotoListView.as_view(),
        name='tracker_company_company_private_public_photo_list'
    ),
    url(
        r'^company/total_photo_size/$',
        tracker_views.TrackerCompanyTotalPhotoSizeListView.as_view(),
        name='tracker_company_total_photo_size'
    ),
    url(
        r'^company/project_photo_list/$',
        tracker_views.TrackerCompanyProjectPhotoListView.as_view(),
        name='tracker_company_project_photo_list'
    ),
    url(
        r'^company/bom_photo_list/$',
        tracker_views.TrackerCompanyBomPhotoListView.as_view(),
        name='tracker_company_bom_photo_list'
    ),
    url(
        r'^company/video_list/$',
        tracker_views.TrackerCompanyVideoListView.as_view(),
        name='tracker_company_video_list'
    ),
    url(
        r'^company/company_video_list/$',
        tracker_views.TrackerCompanyCompanyVideoListView.as_view(),
        name='tracker_company_company_video_list'
    ),
    url(
        r'^company/total_video_size/$',
        tracker_views.TrackerCompanyTotalVideoSizeListView.as_view(),
        name='tracker_company_total_video_size'
    ),
    url(
        r'^company/company_video_list/(?P<type>(private|public){1})/$',
        tracker_views.TrackerCompanyCompanyVideoListView.as_view(),
        name='tracker_company_company_private_public_video_list'
    ),
    url(
        r'^company/project_video_list/$',
        tracker_views.TrackerCompanyProjectVideoListView.as_view(),
        name='tracker_company_project_video_list'
    ),
    url(
        r'^company/bom_video_list/$',
        tracker_views.TrackerCompanyBomVideoListView.as_view(),
        name='tracker_company_bom_video_list'
    ),
    url(
        r'^company/bom_list/$',
        tracker_views.TrackerCompanyBomListView.as_view(),
        name='tracker_company_bom_list'
    ),
    url(
        r'^company/quotation_list/$',
        tracker_views.TrackerCompanyQuotationListView.as_view(),
        name='tracker_company_quotation_list'
    ),
    url(
        r'^company/offer_list/$',
        tracker_views.TrackerCompanyOfferListView.as_view(),
        name='tracker_company_offer_list'
    ),
    url(
        r'^company/active_offer_list/$',
        tracker_views.TrackerCompanyActiveOfferListView.as_view(),
        name='tracker_company_active_offer_list'
    ),
    url(
        r'^company/certification_list/$',
        tracker_views.TrackerCompanyCertificationListView.as_view(),
        name='tracker_company_certification_list'
    ),
    url(
        r'^company/phantom_list/$',
        tracker_views.TrackerCompanyPhantomListView.as_view(),
        name='tracker_company_phantom_list'
    ),
    url(
        r'^company/guest_list/$',
        tracker_views.TrackerCompanyGuestListView.as_view(),
        name='tracker_company_guest_list'
    ),
    url(
        r'^company/(?P<type>(request|approve|refuse|waiting){1})/staff_list/$',
        tracker_views.TrackerCompanyStaffListView.as_view(),
        name='tracker_company_staff_list'
    ),
    url(
        r'^company/(?P<type>(request|approve|refuse|waiting){1})/staff_list_and_external/$',
        tracker_views.TrackerCompanyStaffListAndExternalView.as_view(),
        name='tracker_company_staff_list_and_external'
    ),
    url(
        r'^company/(?P<type>(request|approve|refuse|waiting){1})/staff_list/disabled/$',
        tracker_views.TrackerCompanyStaffListDisabledView.as_view(),
        name='tracker_company_staff_list_disabled'
    ),
    url(
        r'^company/public_staff_list/$',
        tracker_views.TrackerCompanyPublicStaffListView.as_view(),
        name='tracker_company_public_staff_list'
    ),
    url(
        r'^company/showroom_staff_list/$',
        tracker_views.TrackerCompanyShowroomStaffListView.as_view(),
        name='tracker_company_showroom_staff_list'
    ),
    url(
        r'^company/owner_list/$',
        tracker_views.TrackerCompanyOwnerListView.as_view(),
        name='tracker_company_owner_list'
    ),
    url(
        r'^company/delegate_list/$',
        tracker_views.TrackerCompanyDelegateListView.as_view(),
        name='tracker_company_delegate_list'
    ),
    url(
        r'^company/level1_list/$',
        tracker_views.TrackerCompanyLevel1ListView.as_view(),
        name='tracker_company_level1_list'
    ),
    url(
        r'^company/level2_list/$',
        tracker_views.TrackerCompanyLevel2ListView.as_view(),
        name='tracker_company_level2_list'
    ),
    url(
        r'^company/project_list/$',
        tracker_views.TrackerCompanyProjectListView.as_view(),
        name='tracker_company_project_list'
    ),
    url(
        r'^company/simple_project_list/$',
        tracker_views.TrackerCompanySimpleProjectListView.as_view(),
        name='tracker_company_simple project_list'
    ),
    url(
        r'^company/internal_project_list/$',
        tracker_views.TrackerCompanyInternalProjectListView.as_view(),
        name='tracker_company_internal_project_list'
    ),
    url(
        r'^company/shared_project_list/$',
        tracker_views.TrackerCompanySharedProjectListView.as_view(),
        name='tracker_company_shared_project_list'
    ),
    url(
        r'^company/internal_gantt_list/$',
        tracker_views.TrackerCompanyInternalGanttListView.as_view(),
        name='tracker_company_internal_gantt_list'
    ),
    url(
        r'^company/shared_gantt_list/$',
        tracker_views.TrackerCompanySharedGanttListView.as_view(),
        name='tracker_company_shared_gantt_list'
    ),
    url(
        r'^company/favourite_list/$',
        tracker_views.TrackerCompanyFavouriteListView.as_view(),
        name='tracker_company_favourite_list'
    ),
    url(
        r'^company/favourite_list/waiting/$',
        tracker_views.TrackerCompanyFavouriteWaitingListView.as_view(),
        name='tracker_company_favourite_waiting_list'
    ),
    url(
        r'^company/favourite_list/received/$',
        tracker_views.TrackerCompanyFavouriteReceivedListView.as_view(),
        name='tracker_company_favourite_received_list'
    ),
    url(
        r'^company/not_favourite_list/$',
        tracker_views.TrackerCompanyNotFavouriteListView.as_view(),
        name='tracker_company_not_favourite_list'
    ),
    url(
        r'^company/favourites/contact_list/$',
        tracker_views.TrackerCompanyFavouriteContactListView.as_view(),
        name='tracker_company_favourite_contact_list'
    ),
    url(
        r'^company/favourite/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyFavouriteDetailView.as_view(),
        name='tracker_company_favourite_detail'
    ),
    url(
        r'^company/favourite/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerCompanyFavouriteDeleteView.as_view(),
        name='tracker_company_favourite_delete'
    ),

    url(
        r'^profile/activity/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerProfileActivityIntervalDetailView.as_view(),
        name='tracker_profile_activity_interval_detail'
    ),
    url(
        r'^profile/project/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerProfileProjectIntervalDetailView.as_view(),
        name='tracker_company_profile_project_interval_detail'
    ),

    url(
        r'^company/staff/activity/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerCompanyStaffActivityIntervalDetailView.as_view(),
        name='tracker_company_staff_activity_interval_detail'
    ),

    url(
        r'^company/project/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerCompanyProjectIntervalDetailView.as_view(),
        name='tracker_company_project_interval_detail'
    ),
    url(
        r'^profile/message_list/$',
        tracker_views.TrackerProfileMessageListView.as_view(),
        name='tracker_profile_message_list'
    ),
    url(
        r'^profile/to_profile/(?P<profile>\d+)/message_list/$',
        tracker_views.TrackerProfileToProfileMessageListView.as_view(),
        name='tracker_profile_to_profile_message_list'
    ),
    url(
        r'^sponsor/list/$',
        tracker_views.TrackerSponsorListView.as_view(),
        name='tracker_sponsor_List_view'
    ),
    url(
        r'^company/sponsor/active/list/$',
        tracker_views.TrackerCompanySponsorActiveListView.as_view(),
        name='tracker_company_sponsor_active_list_view'
    ),
    url(
        r'^sponsor/add/$',
        tracker_views.TrackerSponsorAddView.as_view(),
        name='tracker_sponsor_add_view'
    ),
    url(
        r'^sponsor/(?P<pk>\d+)/$',
        tracker_views.TrackerSponsorDetailView.as_view(),
        name='tracker_sponsor_detail_view'
    ),
    url(
        r'^sponsor/(?P<pk>\d+)/edit/$',
        tracker_views.TrackerSponsorEditView.as_view(),
        name='tracker_sponsor_edit'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
