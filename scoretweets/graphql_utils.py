import time
import json

FACEBOOK_GRAPH_URL = 'https://www.facebook.com/api/graphql/'

class FacebookGraph:
    REQ_FRIENDLY_NAMES = {
        'post': 'ComposerStoryCreateMutation',
        'delete': 'useCometFeedStoryDeleteMutation'
    }

    DOC_ID = {
        'post': '9393079900709467',
        'delete': '6322833501068172'
    }

    def __init__(self, group_id, actor_id, env):
        self.__env = env
        self.__group_id = group_id
        self.__actor_id = actor_id
        self.__referer = f'https://www.facebook.com/groups/{group_id}/'

    def __prepare_post_variables(self, text):
        return {
            'input': {
                'composer_entry_point':'inline_composer',
                'composer_source_surface':'group',
                'composer_type':'group',
                'logging': None,
                'source':'WWW',
                'attachments':[],
                'message':{
                    'ranges':[],
                    'text': text
                    },
                'with_tags_ids':[],
                'inline_activities':[],
                'explicit_place_id':'0',
                'text_format_preset_id':'0',
                'navigation_data':{
                    'attribution_id_v2': f'CometGroupDiscussionRoot.react,comet.group,via_cold_start,{int(time.time()*1000)},919590,2361831622,'
                    },
                'tracking':[None],
                'audience':{'to_id': self.__group_id},
                'actor_id': self.__actor_id,
                'client_mutation_id':'1'
                },
            'displayCommentsFeedbackContext': None,
            'displayCommentsContextEnableComment':None,
            'displayCommentsContextIsAdPreview':None,
            'displayCommentsContextIsAggregatedShare':None,
            'displayCommentsContextIsStorySet':None,
            'feedLocation':'GROUP',
            'feedbackSource':0,
            'focusCommentID':None,
            'gridMediaWidth':None,
            'groupID':None,
            'scale':1,
            'privacySelectorRenderLocation':'COMET_STREAM',
            'renderLocation':'group',
            'useDefaultActor':False,
            'inviteShortLinkKey':None,
            'isFeed':False,
            'isFundraiser':False,
            'isFunFactPost':False,
            'isGroup':True,
            'isEvent':False,
            'isTimeline':False,
            'isSocialLearning':False,
            'isPageNewsFeed':False,
            'isProfileReviews':False,
            'isWorkSharedDraft':False,
            'UFI2CommentsProvider_commentsKey':'CometGroupDiscussionRootSuccessQuery',
            'hashtag':None,
            'canUserManageOffers':False,
            '__relay_internal__pv__StoriesRingrelayprovider':False,
            '__relay_internal__pv__IsWorkUserrelayprovider':False
        }

    def __prepare_delete_variables(self, story_id):
        return {
            'input':{
                'story_id':story_id,
                'story_location':'PERMALINK',
                'actor_id': self.__actor_id,
                'client_mutation_id':'1'
            },
            'groupID': None,
            'inviteShortLinkKey': None,
            'renderLocation': None,
            'scale': 1
        }

    def __prepare_data(self, variables, fb_api_req_friendly_name, doc_id):
        return {
            'av': self.__actor_id,
            '__user': self.__actor_id,
            '__a': '1',
            '__dyn': '',
            '__csr': '',
            '__req': 'n',
            '__hs': '19390.HYP:comet_pkg.2.1.0.2.1',
            'dpr': '1',
            '__ccg': 'GOOD',
            '__rev': self.__env['data_btmanifest'],
            '__s': '1:1',
            '__hsi': self.__env['cavalry_get_lid'],
            '__comet_req': '15',
            'fb_dtsg': self.__env['dtsg'],
            'jazoest': self.__env['jazoest'],
            '__spin_r': self.__env['data_btmanifest'],
            '__spin_b': 'trunk',
            '__spin_t': int(time.time()),
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': fb_api_req_friendly_name,
            'server_timestamps': True,
            'doc_id': doc_id,
            'fb_api_analytics_tags': '[]',
            'variables': json.dumps(variables)
        }

    def get_post_query(self, text):
        variables = self.__prepare_post_variables(text)
        data = self.__prepare_data(variables, self.REQ_FRIENDLY_NAMES['post'], self.DOC_ID['post'])
        headers = {
            'X-Fb-Friendly-Name': self.REQ_FRIENDLY_NAMES['post'],
            'Referer': self.__referer
        }
        return headers, data

    def get_delete_query(self, story_id):
        variables = self.__prepare_delete_variables(story_id)
        data = self.__prepare_data(variables, self.REQ_FRIENDLY_NAMES['delete'], self.DOC_ID['delete'])
        headers = {
            'X-Fb-Friendly-Name': self.REQ_FRIENDLY_NAMES['delete'],
            'Referer': self.__referer
        }
        return headers, data
