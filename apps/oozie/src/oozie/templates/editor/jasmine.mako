<%inherit file="/common_jasmine.mako"/>

<%block name="specs">
  <script src="${ STATIC_URL }/desktop/ext/js/knockout.mapping-2.3.2.js" type="text/javascript" charset="utf-8"></script>
  <script src="${ STATIC_URL }/desktop/ext/js/moment.min.js" type="text/javascript" charset="utf-8"></script>
  <script src="${ STATIC_URL }/desktop/ext/js/bootstrap.min.js" type="text/javascript" charset="utf-8"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.utils.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.registry.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.modal.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.models.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.idgen.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.node-fields.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.node.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.js"></script>
  <script type="text/javascript" src="${ STATIC_URL }/oozie/js/workflow.import-node.js"></script>
  <script src="${ STATIC_URL }/oozie/jasmine/workflow.js" type="text/javascript" charset="utf-8"></script>
</%block>

<%block name="fixtures">
  <div style="display:none">
    <h1>Buongiorno, world!</h1>
    <div id="graph"></div>
  </div>

  <div id="modal-window" class="modal hide fade">
    <a class="doneButton"></a>
    <a class="cancelButton"></a>
    <a class="closeButton"></a>
  </div>
</%block>
