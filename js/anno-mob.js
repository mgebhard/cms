var ANNOTATOR;

annotorious.plugin.MobPlugin = function(opt_config_options) { }

annotorious.plugin.MobPlugin.prototype.initPlugin = function(anno) {
  // Add initialization code here, if needed (or just skip this method if not)
}

annotorious.plugin.MobPlugin.prototype.onInitAnnotator = function(annotator) {
    // A Field can be an HTML string or a function(annotation) that returns a string
    annotator.popup.addField(function(annotation) { 
    return '<em>Hello World: ' + annotation.text.length + ' chars</em>'
    });

    // Override to not show editor
    annotator.editor.__proto__.open = function() {
      console.log("no editor for you!");
    }
    
    ANNOTATOR = annotator;
}