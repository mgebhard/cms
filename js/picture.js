var NEW_COMMENT;

anno.setProperties({
    fill: "rgba(243, 40, 55, 0.69)"
});

window.blockMenuHeaderScroll = false;
jQuery(window).on('touchstart', function(e)
{
    //console.log(e.target);
    if (jQuery(e.target).closest('canvas.annotorious-item').length == 1)
    {
        blockMenuHeaderScroll = true;
    }
});
jQuery(window).on('touchend', function()
{
    blockMenuHeaderScroll = false;
});
jQuery(window).on('touchmove', function(e)
{
    if (blockMenuHeaderScroll)
    {
        e.preventDefault();
    }
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
        // TODO: being fired more than once?!
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
        $('.new-comment-div').css("display", "flex");

        // allow annotating
        //anno.hideAnnotations();
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
            center : {x: (x+(x+width))/2.0, y: (y+(y+height))/2.0},
            user : $this.data('user'),
            anonymous: $('.anon-checkbox[name="anon"]').is(':checked'),
            art_id: $this.data('art-id')
        }

        var req = $.post('http://artannotator.appspot.com/mfa/' + annotation.art_id,
                         {data: JSON.stringify(annotation)});

        req.done(function(data) {
            console.log("Success!");
            console.log(data);
            anno.addAnnotation(annotation);


            ANNOTATOR.fireEvent('onAnnotationCreated', annotation);


            //add to art comments in dom
            var newComment = $('.art-comment').first().clone();
            var newName = annotation.anonymous ? 'Anonymous' : annotation.user;
            newComment.find('.comment-name').text(newName);
            newComment.find('.comment-text').text(annotation.text);
            newComment.find('.comment-time').text(data.time_posted);

            $('.art-comment-header').after(newComment);


        }).fail(function(jqxhr) {
            console.log(jqxhr);
            alert("Failure");
        }).always(function() {
            $('.type-comment').hide();
            $('.new-show-buttons').show();

            ANNOTATOR.stopSelection();
            anno.hideSelectionWidget();
            anno.hideAnnotations();
        });



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
        anno.hideAnnotations();
        anno.hideSelectionWidget();

    });

    //add annotations
    document.addEventListener("annotatorLoaded", function() {
        console.log('event fired');
        addAnnotations(annotationsJSON);
    }, false);

});

function filterAnnotations(rect) {
    var annotations = anno.getAnnotations();
    for(var i = 0 , len = annotations.length; i<len; i++) {
        var comment = annotations[i];
        var center = comment.center;
        console.log(center);
        console.log(rect);
        if (center.x >= rect.x &&
            center.x <= rect.x + rect.width &&
            center.y >= rect.y &&
            center.y <= rect.y + rect.height) {

            jQuery('.art-comment[data-user="'+ comment.user + '"]').show();
        }
        else {
            jQuery('.art-comment[data-user="'+ comment.user + '"]').hide();
        }
    }
}

function addAnnotations(annoJSON) {
    //var ANNOTATOR = ANNOTATOR;
    annoJSON.forEach(function(annotation) {
        // Turn to front-end format
        var newAnno = {
            /** The URL of the image where the annotation should go **/
           src : jQuery('.art-image').attr('src'),
           /** The annotation text **/
           text : annotation.text,
           /** The annotation shape **/
           shapes : [{
               /** The shape type **/
               type : 'rect',
               /** The shape geometry (relative coordinates) **/
               geometry : {
                   x : annotation.x_cord,
                   y: annotation.y_cord,
                   width : annotation.width,
                   height: annotation.height
               }
           }],
           center : {x: annotation.center_x, y: annotation.center_y},
           user : annotation.annotator,
           anonymous: annotation.anonymous,
           art_id: annotation.art_id
        }
        console.log(newAnno);
        // add
        anno.addAnnotation(newAnno);
        anno.hideAnnotations();
        console.log(anno.getAnnotations());
        ANNOTATOR.fireEvent('onAnnotationCreated', annotation);
    })
}
