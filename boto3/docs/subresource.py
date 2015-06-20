# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from botocore import xform_name

from boto3.docs.base import BaseDocumenter
from boto3.docs.utils import get_identifier_args_for_signature
from boto3.docs.utils import get_identifier_values_for_example
from boto3.docs.utils import get_identifier_description
from boto3.docs.utils import add_resource_type_overview


class SubResourceDocumenter(BaseDocumenter):
    def document_sub_resources(self, section):
        add_resource_type_overview(
            section=section,
            resource_type='Sub-resources',
            description=(
                'Sub-resources are methods that create a new instance of a'
                ' child resource. This resource\'s identifiers get passed'
                ' along to the child.'),
            intro_link='subresources_intro')
        sub_resources = sorted(
            self._resource.meta.resource_model.subresources,
            key=lambda sub_resource: sub_resource.name
        )
        sub_resources_list = []
        self.member_map['sub-resources'] = sub_resources_list
        for sub_resource in sub_resources:
            sub_resource_section = section.add_new_section(sub_resource.name)
            sub_resources_list.append(sub_resource.name)
            self._document_sub_resource(sub_resource_section, sub_resource)

    def _document_sub_resource(self, sub_resource_section, sub_resource):
        identifiers_needed = []
        for identifier in sub_resource.resource.identifiers:
            if identifier.source == 'input':
                identifiers_needed.append(xform_name(identifier.target))

        signature_args = get_identifier_args_for_signature(identifiers_needed)
        sub_resource_section.style.start_sphinx_py_method(
            sub_resource.name, signature_args)

        method_intro_section = sub_resource_section.add_new_section(
            'method-intro')
        description = 'Creates a %s resource.' % sub_resource.resource.type
        method_intro_section.include_doc_string(description)

        example_section = sub_resource_section.add_new_section('example')
        example_values = get_identifier_values_for_example(identifiers_needed)
        resource_name = xform_name(self._resource_name)
        if self.represents_service_resource:
            resource_name = self._resource_name
        example = '%s = %s.%s(%s)' % (
            xform_name(sub_resource.resource.type),
            resource_name,
            sub_resource.name, example_values
        )
        example_section.style.start_codeblock()
        example_section.write(example)
        example_section.style.end_codeblock()

        param_section = sub_resource_section.add_new_section('params')
        for identifier in identifiers_needed:
            description = get_identifier_description(
                sub_resource.name, identifier)
            param_section.write(':type %s: string' % identifier)
            param_section.style.new_line()
            param_section.write(':param %s: %s' % (
                identifier, description))
            param_section.style.new_line()

        return_section = sub_resource_section.add_new_section('return')
        return_section.style.new_line()
        return_section.write(
            ':rtype: :py:class:`%s.%s`' % (
                self._service_docs_name, sub_resource.resource.type))
        return_section.style.new_line()
        return_section.write(
            ':returns: A %s resource' % sub_resource.resource.type)
        return_section.style.new_line()