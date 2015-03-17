# oppia/api/serializers.py
import json

from tastypie.serializers import Serializer

class PrettyJSONSerializer(Serializer):
    json_indent = 4

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return json.dumps(data,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)

class UserJSONSerializer(Serializer):     
    json_indent = 0

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        if 'objects' in data:
            data['users'] = data['objects']
            del data['objects']
        return json.dumps(data,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)
          
class CourseJSONSerializer(Serializer):
    json_indent = 0
    
    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
    
        if 'objects' in data:
            data['courses'] = data['objects']
            del data['objects']

        return json.dumps(data,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)


class ClientJSONSerializer(Serializer):
    json_indent = 0
    formats = ['json']
    content_types = {
        'json': 'application/json',
    }

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)

        if 'objects' in data:
            data['clients'] = data['objects']
            del data['objects']
        data = {'clients': data['clients'], 'previousSyncTime': data['previousSyncTime']}

        return json.dumps(data,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)


class ClientTrackerJSONSerializer(Serializer):
    json_indent = 0
    formats = ['json']
    content_types = {
        'json': 'application/json',
    }

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)

        if 'objects' in data:
            data['sessions'] = data['objects']
            del data['objects']
        data = {'sessions': data['sessions']}

        return json.dumps(data,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)
