# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import tracker_views


user_urlpatterns = []

generic_urlpatterns = []

tracker_urlpatterns = [
    url(
        r'^project/parent/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectParentDetailView.as_view(),
        name='tracker_project_parent_detail'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/message_list/$',
        tracker_views.TrackerProjectParentMessageListView.as_view(),
        name='tracker_project_parent_message_list'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/team_list/$',
        tracker_views.TrackerProjectParentTeamListView.as_view(),
        name='tracker_project_parent_team_list'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/task_list/$',
        tracker_views.TrackerProjectParentTaskListView.as_view(),
        name='tracker_project_parent_task_list'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/activity_list/$',
        tracker_views.TrackerProjectParentActivityListView.as_view(),
        name='tracker_project_parent_activity_list'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/document_list/$',
        tracker_views.TrackerProjectParentDocumentListView.as_view(),
        name='tracker_project_parent_document_list'
    ),
    url(
        r'^project/parent/(?P<pk>\d+)/gantt/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerProjectParentGanttIntervalDetailView.as_view(),
        name='tracker_project_parent_gantt_interval_detail'
    ),
    url(
        r'^project/$',
        tracker_views.TrackerProjectListView.as_view(),
        name='tracker_project_list'
    ),
    url(
        r'^activity/post_list_alert/$',
        tracker_views.TrackerActivityPostListAlertView.as_view(),
        name='tracker_activity_post_list_alert'
    ),
    url(
        r'^task/post_list_alert/$',
        tracker_views.TrackerTaskPostListAlertView.as_view(),
        name='tracker_task_post_list_alert'
    ),
    url(
        r'^project/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDetailView.as_view(),
        name='tracker_project_detail'
    ),
    url(
        r'^project/add/$',
        tracker_views.TrackerProjectAddView.as_view(),
        name='tracker_project_add'
    ),
    url(
        r'^project/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectEditView.as_view(),
        name='tracker_project_edit'
    ),
    url(
        r'^project/enable/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectEnableView.as_view(),
        name='tracker_project_enable'
    ),
    url(
        r'^project/disable/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDisableView.as_view(),
        name='tracker_project_disable'
    ),
    url(
        r'^project/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectDeleteView.as_view(),
        name='tracker_project_delete'
    ),
    url(
        r'^project/share/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectShareView.as_view(),
        name='tracker_project_share'
    ),
    url(
        r'^project/(?P<pk>\d+)/team_add/$',
        tracker_views.TrackerProjectTeamAddView.as_view(),
        name='tracker_project_team_add'
    ),
    url(
        r'^project/(?P<pk>\d+)/generate_code/$',
        tracker_views.TrackerProjectGenerateCodeView.as_view(),
        name='tracker_project_team_generate_code'
    ),
    url(
        r'^project/add_team_by_code/$',
        tracker_views.TrackerProjectAddTeamByCodeView.as_view(),
        name='tracker_project_add_team_by_code'
    ),
    
    # url(
    #     r'^project/invite/profile_add/(?P<pk>\d+)/$',
    #     tracker_views.TrackerProjectInviteProfileAddView.as_view(),
    #     name='tracker_invite_company_profile_add'
    # ),
    # url(
    #     r'^project/(?P<type>(request|approve|refuse|waiting){1})/staff_list/$',
    #     tracker_views.TrackerProjectStaffListView.as_view(),
    #     name='tracker_company_staff_list'
    # ),
    url(
        r'^project/(?P<pk>\d+)/task_add/$',
        tracker_views.TrackerProjectTaskAddView.as_view(),
        name='tracker_project_task_add'
    ),
    url(
        r'^project/(?P<pk>\d+)/bom_sender_list/$',
        tracker_views.TrackerProjectBomSenderListView.as_view(),
        name='tracker_project_bom_sender_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/bom_draft_list/$',
        tracker_views.TrackerProjectBomDraftListView.as_view(),
        name='tracker_project_bom_draft_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/bom_receiver_list/$',
        tracker_views.TrackerProjectBomReceiverListView.as_view(),
        name='tracker_project_bom_receiver_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/quotation_sender_list/$',
        tracker_views.TrackerProjectQuotationSenderListView.as_view(),
        name='tracker_project_quotation_sender_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/quotation_receiver_list/$',
        tracker_views.TrackerProjectQuotationReceiverListView.as_view(),
        name='tracker_project_quotation_receiver_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/quotation_draft_list/$',
        tracker_views.TrackerProjectQuotationDraftListView.as_view(),
        name='tracker_project_quotation_draft_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/internal_activity_list/$',
        tracker_views.TrackerProjectInternalActivityListView.as_view(),
        name='tracker_project_internal_activity_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/activity_list/$',
        tracker_views.TrackerProjectActivityListView.as_view(),
        name='tracker_project_activity_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/team_list/$',
        tracker_views.TrackerProjectTeamListView.as_view(),
        name='tracker_project_team_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/(?P<type>(request|approve|refuse|waiting){1})/team_list/$',
        tracker_views.TrackerProjectTeamListView.as_view(),
        name='tracker_project_team_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/talk_list/$',
        tracker_views.TrackerProjectTalkListView.as_view(),
        name='tracker_project_talk_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/message_list/$',
        tracker_views.TrackerProjectMessageListView.as_view(),
        name='tracker_project_message_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/photo_list/$',
        tracker_views.TrackerProjectPhotoListView.as_view(),
        name='tracker_project_photo_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/video_list/$',
        tracker_views.TrackerProjectVideoListView.as_view(),
        name='tracker_project_video_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/folder_list/$',
        tracker_views.TrackerProjectPhotoListView.as_view(),
        name='tracker_project_folder_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/internal_task_list/$',
        tracker_views.TrackerProjectInternalTaskListView.as_view(),
        name='tracker_project_internal_task_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/task_list/$',
        tracker_views.TrackerProjectTaskListView.as_view(),
        name='tracker_project_task_list'
    ),
    url(
        r'^gantt/project/(?P<pk>\d+)/task_list/$',
        tracker_views.TrackerGanttProjectTaskListView.as_view(),
        name='tracker_gantt_project_task_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/document_list/$',
        tracker_views.TrackerProjectDocumentListView.as_view(),
        name='tracker_project_document_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/showcase_list/$',
        tracker_views.TrackerProjectShowCaseListView.as_view(),
        name='tracker_project_showcase_list'
    ),
    url(
        r'^project/(?P<pk>\d+)/gantt/(?P<month>\d+)/(?P<year>\d+)/$',
        tracker_views.TrackerProjectGanttIntervalDetailView.as_view(),
        name='tracker_project_gantt_interval_detail'
    ),
    url(
        r'^project/(?P<pk>\d+)/internal_gantt/$',
        tracker_views.TrackerProjectInternalGanttDetailView.as_view(),
        name='tracker_project_internal_gantt_detail'
    ),
    url(
        r'^project/(?P<pk>\d+)/gantt/$',
        tracker_views.TrackerProjectGanttDetailView.as_view(),
        name='tracker_project_gantt_detail'
    ),
    url(
        r'^task/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskDetailView.as_view(),
        name='tracker_task_detail'
    ),
    url(
        r'^task/share/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskShareView.as_view(),
        name='tracker_task_share'
    ),
    url(
        r'^task/clone/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskCloneView.as_view(),
        name='tracker_task_clone'
    ),
    url(
        r'^task/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskEditView.as_view(),
        name='tracker_task_edit'
    ),
    url(
        r'^task/enable/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskEnableView.as_view(),
        name='tracker_task_enable'
    ),
    url(
        r'^task/disable/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskDisableView.as_view(),
        name='tracker_task_disable'
    ),
    url(
        r'^task/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerTaskDeleteView.as_view(),
        name='tracker_task_delete'
    ),
    url(
        r'^team/inviation_list/$',
        tracker_views.TrackerTeamInviationListView.as_view(),
        name='tracker_team_detail'
    ),
    url(
        r'^team/(?P<pk>\d+)/$',
        tracker_views.TrackerTeamDetailView.as_view(),
        name='tracker_team_detail'
    ),
    url(
        r'^team/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerTeamEditView.as_view(),
        name='tracker_team_edit'
    ),
    url(
        r'^team/enable/(?P<pk>\d+)/$',
        tracker_views.TrackerTeamEnableView.as_view(),
        name='tracker_team_enable'
    ),
    url(
        r'^team/disable/(?P<pk>\d+)/$',
        tracker_views.TrackerTeamDisableView.as_view(),
        name='tracker_team_disable'
    ),
    url(
        r'^team/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerTeamDeleteView.as_view(),
        name='tracker_team_delete'
    ),
    url(
        r'^task/(?P<pk>\d+)/attachment_add/$',
        tracker_views.TrackerTaskAttachmentAddView.as_view(),
        name='tracker_task_attachment_add'
    ),
    url(
        r'^task/(?P<pk>\d+)/attachment_download/(?P<pk2>\d+)/$',
        tracker_views.TrackerTaskAttachmentDownloadView.as_view(),
        name='tracker_task_attachment_add'
    ),
    url(
        r'^attachment/(?P<pk>\d+)/delete/$',
        tracker_views.TrackerAttachmentDeleteView.as_view(),
        name='tracker_attachment_delete'
    ),
    url(
        r'^task/(?P<pk>\d+)/activity_add/$',
        tracker_views.TrackerTaskActivityAddView.as_view(),
        name='tracker_task_activity_add'
    ),
    url(
        r'^task/(?P<pk>\d+)/activity_list/$',
        tracker_views.TrackerTaskActivityListView.as_view(),
        name='tracker_task_activity_list'
    ),
    url(
        r'^activity/(?P<pk>\d+)/$',
        tracker_views.TrackerActivityDetailView.as_view(),
        name='tracker_activity_detail'
    ),
    url(
        r'^activity/status/(?P<pk>\d+)/$',
        tracker_views.TrackerActivityEditStatusView.as_view(),
        name='tracker_activity_edit_status'
    ),
    url(
        r'^activity/edit/(?P<pk>\d+)/$',
        tracker_views.TrackerActivityEditView.as_view(),
        name='tracker_activity_edit'
    ),
    url(
        r'^activity/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerActivityDeleteView.as_view(),
        name='tracker_activity_delete'
    ),
    url(
        r'^activity/(?P<pk>\d+)/post_list/$',
        tracker_views.TrackerActivityPostListView.as_view(),
        name='tracker_activity_post_list'
    ),
    url(
        r'^task/(?P<pk>\d+)/post_list/$',
        tracker_views.TrackerTaskPostListView.as_view(),
        name='tracker_task_post_list'
    ),
    url(
        r'^activity/(?P<pk>\d+)/add_post/$',
        tracker_views.TrackerActivityPostAddView.as_view(),
        name='tracker_activity_post_add'
    ),
    url(
        r'^task/(?P<pk>\d+)/add_post/$',
        tracker_views.TrackerTaskPostAddView.as_view(),
        name='tracker_task_post_add'
    ),
    url(
        r'^post/(?P<pk>\d+)/edit/$',
        tracker_views.TrackerPostEditView.as_view(),
        name='tracker_edit_post'
    ),
    url(
        r'^post/(?P<pk>\d+)/notify/$',
        tracker_views.TrackerPostNotifyView.as_view(),
        name='tracker_notify_post'
    ),
    url(
        r'^post/(?P<pk>\d+)/comment_list/$',
        tracker_views.TrackerPostCommentListView.as_view(),
        name='tracker_post_comment_list'
    ),
    url(
        r'^post/(?P<pk>\d+)/add_comment/$',
        tracker_views.TrackerPostCommentAddView.as_view(),
        name='tracker_activity_comment_add'
    ),
    url(
        r'^comment/(?P<pk>\d+)/edit/$',
        tracker_views.TrackerCommentEditView.as_view(),
        name='tracker_edit_comment'
    ),
    url(
        r'^post/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerPostDeleteView.as_view(),
        name='tracker_post_delete'
    ),
    url(
        r'^comment/delete/(?P<pk>\d+)/$',
        tracker_views.TrackerCommentDeleteView.as_view(),
        name='tracker_comment_delete'
    ),
    url(
        r'^comment/(?P<pk>\d+)/replies_list/$',
        tracker_views.TrackerCommentRepliesListView.as_view(),
        name='tracker_comment_replies_list'
    ),
    url(
        r'^post/(?P<pk>\d+)/share_to_task/$',
        tracker_views.TrackerSharePostToTaskView.as_view(),
        name='tracker_activity_task_post_share'
    ),
    url(
        r'^task/(?P<pk>\d+)/shared_posts/$',
        tracker_views.TrackerTaskPostsListView.as_view(),
        name='tracker_activity_task_posts'
    ),
    url(
        r'^photo/download/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectPhotoDownloadView.as_view(),
        name='tracker_project_document_download'
    ),
    url(
        r'^video/download/(?P<pk>\d+)/$',
        tracker_views.TrackerProjectVideoDownloadView.as_view(),
        name='tracker_project_document_download'
    ),
    url(
        r'^project/(?P<pk>\d+)/export/$',
        tracker_views.TrackerProjectExport.as_view(),
        name='tracker_project_export'
    ),
]

urlpatterns = user_urlpatterns + generic_urlpatterns + tracker_urlpatterns
