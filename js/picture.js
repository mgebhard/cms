var NEW_COMMENT;

anno.setProperties({
    fill: 'red'
});

//no annotating by default
anno.hideSelectionWidget();

anno.addHandler('onAnnotationCreated', function(annotation) {
    console.log(annotation.text);
});

anno.addHandler('onSelectionCompleted', function(event) {
    if (NEW_COMMENT) {
        // Show form, hide other div
        jQuery('.new-comment-div').hide();
        jQuery('.type-comment').show();
        console.log(event);
        // Add coord info as data attributes of form
        jQuery('#comment-form').data('x-coord', event.shape.geometry.x);
        jQuery('#comment-form').data('y-coord',event.shape.geometry.y);
        jQuery('#comment-form').data('rect-width',event.shape.geometry.width);
        jQuery('#comment-form').data('rect-height',event.shape.geometry.height);
    }
    else {
        // Restore .new-show-buttons and hide
        jQuery('.show-comments').show();
        jQuery('.hide-comments').hide();
        jQuery('.show-comment-how').hide();
        jQuery('.new-show-buttons').hide();
        // Show list of annotations
        filterAnnotations(event.shape.geometry);
        jQuery('.show-comment-div').show();
    }
});

jQuery.noConflict();

jQuery(document).ready(function($) {

    $('.show-comments').click(function() {
        NEW_COMMENT = false;
        $(this).hide();
        $('.hide-comments').show();
        $('.show-comment-how').show();

        anno.showAnnotations();
        anno.showSelectionWidget();
    });

    $('.hide-comments').click(function() {
        $(this).hide();
        $('.show-comments').show();
        $('.show-comment-how').hide();

        anno.hideAnnotations();
        anno.hideSelectionWidget();
    });

    $('.new-comment').click(function() {
        NEW_COMMENT = true;
        $(this).parent().hide();
        $('.new-comment-div').show();

        // allow annotating
        anno.showSelectionWidget();
    });

    $('.cancel-new').click(function() {
        $(this).parent().hide();
        $('.new-show-buttons').show();

        //no more annotating allowed
        ANNOTATOR.stopSelection();
        anno.hideSelectionWidget();
    });

    $('#comment-form').submit(function(e) {
        e.preventDefault();
        var $this = $(this);
        var x = $this.data('x-coord');
        var y = $this.data('y-coord');
        var width = $this.data('rect-width');
        var height = $this.data('rect-height');
        // Create annotation and make request
        var annotation = {
             /** The URL of the image where the annotation should go **/
            src : $('.art-image').attr('src'),
            /** The annotation text **/
            text : $('.comment-text').val(),
            /** The annotation shape **/
            shapes : [{
                /** The shape type **/
                type : 'rect',
                /** The shape geometry (relative coordinates) **/
                geometry : {
                    x : x,
                    y: y,
                    width : width,
                    height: height
                }
            }],
            center : {x: (x+width)/2.0, y: (y+height)/2.0},
            user_id : $this.data('user-id');
        }

        console.log(annotation);
        anno.addAnnotation(annotation);
        ANNOTATOR.stopSelection();

        ANNOTATOR.fireEvent('onAnnotationCreated', annotation);

        $('.type-comment').hide();
        $('.new-show-buttons').show();

        anno.hideSelectionWidget();
        anno.hideAnnotations();
    });

    $('.cancel-comment').click(function(e) {
        e.preventDefault();

        ANNOTATOR.stopSelection();

        $('.type-comment').hide();
        $('.new-show-buttons').show();

        ANNOTATOR.stopSelection();
        anno.hideSelectionWidget();
    });

    $('.go-back-btn').click(function() {
        $('.show-comment-div').hide();
        $('.new-show-buttons').show();

        ANNOTATOR.stopSelection();
        anno.hideSelectionWidget();

    });
});

function filterAnnotations(rect) {
    var annotations = anno.getAnnotations();
    annotations.forEach(function(comment) {
        var center = comment.center;
        console.log(center.x);
        if (center.x >= rect.x &&
            center.x <= rect.x + rect.width &&
            center.y >= rect.y &&
            center.y <= rect.y + rect.height) {
        
            $('[data-user-id="'+ comment.user_id + '"]').show();
        }
        else {
            $('[data-user-id="'+ comment.user_id + '"]').hide();
        }
    });
}
