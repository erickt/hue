<%namespace name="listDesigns" file="designs.mako" />
<%inherit file="common_jasmine.mako"/>

<%block name="specs">
    <script src="${ STATIC_URL }/desktop/ext/js/mustache.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/desktop/ext/js/routie-0.3.0.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/desktop/ext/js/knockout-min.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/desktop/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/desktop/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/oozie/js/workflow.models.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/oozie/js/workflow.node-fields.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/jobsub/js/jobsub.templates.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/jobsub/js/jobsub.ko.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/jobsub/js/jobsub.js" type="text/javascript" charset="utf-8"></script>
    <script src="${ STATIC_URL }/jobsub/jasmine/jobsubSpec.js"></script>
</%block>


<%block name="fixtures">
  <div style="display:none">
  </div>
</%block>
