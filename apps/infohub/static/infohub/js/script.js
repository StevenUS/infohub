$(document).ready(
    function() {
        // Request the server to grab the article sources.
        $.ajax({
            url: "/info/getinfo",
            method: "get",
            success: function(stories) {
                news = $('#news-box');
                var newsAlerts = 0;

                // For each enabled news source, grab the
                // stories and add them to the home page.
                if(stories["TheGuardian"])
                  newsAlerts += addStoriesToDOM("TheGuardian", stories, news);

                if(stories["CNN"])
                  newsAlerts += addStoriesToDOM("CNN", stories, news);

                if(stories["HuffPost"])
                  newsAlerts += addStoriesToDOM("HuffPost", stories, news);

                // If there were any highlights done, add a news alert.
                if(newsAlerts > 0)
                {
                  $('#alert').text("You have " + newsAlerts + (newsAlerts > 1 ? " news alerts!" : " news alert!"))
                  $('#alert').show();
                }

                // Hide the spinner used while fetching stories.
                $('#loader').attr("hidden", true);
            },
            error: function() {
                $('#news_box').append("<p>\n\rUnable to get news from the selected sources.</p>");
                $('#loader').attr("hidden", true);
            }
        });
        function addStoriesToDOM(location, stories, div){
            var numNewsAlerts = 0;
            
            if(location == "TheGuardian") {
                altLocation = "The Guardian"
            }
            else if (location == "HuffPost"){
                altLocation = "The Huffington Post"
            }
            else { 
                altLocation = location 
            }

            $(div).append("<h4>" + altLocation + "</h4>");

            location = location.replace(" ", "")

            for (var i = 0; i < stories[location].length; i++){
                // Multiple keywords can be highlighted, so handle them separately.
                // Only a comma is currently supported as a keyword delimiter.
                var highlights = [];
                if (stories[location][i].highlight_text)
                  highlights = stories[location][i].highlight_text.split(",");

                // Build the html markup representing the story.
                var html = "<a target='_blank' href=" + stories[location][i].url + ">" + stories[location][i].title + "</a>";
                html += "<p>";

                // Add thumbnail
                image = stories[location][i].image;
                if(image.length === 0 && location === "TheGuardian") {
                    image = $('#guar_def_img').attr('src');
                }
                else if (image.length === 0 && location === "HuffPost") {
                    image = $('#hp_def_img').attr('src');
                }
                else if (image.length === 0 && location === "CNN") {
                    image = $('#cnn_def_img').attr('src');
                }

                html += "<img class='thumbnail' src='" + image + "'>";

                // Highlight each specified keyword.
                var finalDescription = stories[location][i].description;
                var description_length = finalDescription.length;
                for(var k = 0; k < highlights.length; k++)
                {
                    var regex = new RegExp(highlights[k], 'gi' );
                    finalDescription = finalDescription.replace(regex, "<span class='highlight_text'>" + highlights[k] + "</span>");
                }
                html += finalDescription + "</p>";

                // If anything was highligthed, alert the user.
                if(finalDescription.length > description_length)
                    numNewsAlerts++;

                // Add the above html into the DOM.
                $(div).append(html)
            }
            return numNewsAlerts;
            
        }
    });
