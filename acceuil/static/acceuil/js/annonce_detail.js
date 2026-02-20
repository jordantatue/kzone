/* global jQuery */
(function ($) {
    "use strict";

    var annonceDetailModule = {
        init: function () {
            this.$root = $("#annonce-detail-page");
            this.$mainImage = $("#annonce-main-image");
            this.$fullscreenImage = $("#annonce-fullscreen-image");
            this.$statusBadge = $("#annonce-status-badge");
            this.$alerts = $("#annonce-alert-container");
            this.$phoneValue = $("#annonce-phone-value");
            this.actionUrl = this.$root.data("action-url");
            this.bindEvents();
            this.setupCsrfForAjax();
        },

        bindEvents: function () {
            $(document).on("click", ".js-detail-thumb", this.handleThumbnailClick.bind(this));
            $(document).on("show.bs.modal", "#annonceFullscreenModal", this.handleFullscreenOpen.bind(this));
            $(document).on("click", ".js-annonce-action", this.handleActionClick.bind(this));
        },

        setupCsrfForAjax: function () {
            var csrfToken = this.getCookie("csrftoken");
            $.ajaxSetup({
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken || "");
                }
            });
        },

        handleThumbnailClick: function (event) {
            var $button = $(event.currentTarget);
            var imageUrl = $button.data("image-url");
            var imageAlt = $button.data("image-alt") || "Image produit";
            if (!imageUrl) {
                return;
            }
            this.$mainImage.attr("src", imageUrl);
            this.$mainImage.attr("alt", imageAlt);
            $(".js-detail-thumb").removeClass("is-active");
            $button.addClass("is-active");
        },

        handleFullscreenOpen: function () {
            this.$fullscreenImage.attr("src", this.$mainImage.attr("src"));
            this.$fullscreenImage.attr("alt", this.$mainImage.attr("alt"));
        },

        handleActionClick: function (event) {
            var $button = $(event.currentTarget);
            var action = ($button.data("action") || "").trim();
            if (!action || !this.actionUrl) {
                return;
            }

            event.preventDefault();
            var self = this;

            $.ajax({
                url: this.actionUrl,
                method: "POST",
                data: { action: action },
                success: function (response) {
                    if (action === "show_phone") {
                        self.$phoneValue.text(response.phone_number || "");
                        self.$phoneValue.removeClass("d-none");
                        $button.prop("disabled", true).text("Numero affiche");
                    }

                    self.showAlert(response.message || "Action executee.", "success");
                    if (response.redirect_url) {
                        setTimeout(function () {
                            window.location.href = response.redirect_url;
                        }, 700);
                    }
                },
                error: function (xhr) {
                    var payload = xhr.responseJSON || {};
                    if (xhr.status === 401 && payload.login_url) {
                        window.location.href = payload.login_url;
                        return;
                    }
                    self.showAlert(payload.message || "Action impossible pour le moment.", "danger");
                }
            });
        },

        showAlert: function (message, level) {
            var html = "<div class='alert alert-" + level + " alert-dismissible fade show mb-3' role='alert'>"
                + message
                + "<button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Fermer'></button>"
                + "</div>";
            this.$alerts.html(html);
        },

        getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== "") {
                var cookies = document.cookie.split(";");
                for (var i = 0; i < cookies.length; i += 1) {
                    var cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + "=")) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    };

    $(function () {
        if ($("#annonce-detail-page").length > 0) {
            annonceDetailModule.init();
        }
    });
})(jQuery);
