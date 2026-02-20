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
            this.actionUrl = this.$root.data("action-url");
            this.productId = String(this.$root.data("product-id") || "");
            this.favoritesStorageKey = "kzone_favorites";
            this.bindEvents();
            this.setupCsrfForAjax();
            this.syncFavoriteButtons();
        },

        bindEvents: function () {
            $(document).on("click", ".js-detail-thumb", this.handleThumbnailClick.bind(this));
            $(document).on("show.bs.modal", "#annonceFullscreenModal", this.handleFullscreenOpen.bind(this));
            $(document).on("click", ".js-detail-favorite", this.handleFavoriteToggle.bind(this));
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

        handleFavoriteToggle: function (event) {
            event.preventDefault();
            var isFavorite = this.toggleFavoriteState(this.productId);
            this.renderFavoriteState(isFavorite);
            this.showAlert(
                isFavorite ? "Annonce ajoutee aux favoris." : "Annonce retiree des favoris.",
                "success"
            );
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
                    if (response.new_status) {
                        self.$statusBadge.text(response.new_status);
                        self.$statusBadge.removeClass("text-bg-success text-bg-warning text-bg-secondary");
                        if (response.new_status_value === "en_sequestre") {
                            self.$statusBadge.addClass("text-bg-warning");
                            $(".js-annonce-action[data-action='secure_purchase']").prop("disabled", true);
                        } else if (response.new_status_value === "vendu") {
                            self.$statusBadge.addClass("text-bg-secondary");
                            $(".js-annonce-action[data-action='secure_purchase']").prop("disabled", true);
                        } else {
                            self.$statusBadge.addClass("text-bg-success");
                        }
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

        getFavoriteIds: function () {
            try {
                var raw = window.localStorage.getItem(this.favoritesStorageKey);
                var ids = raw ? JSON.parse(raw) : [];
                return Array.isArray(ids) ? ids.map(String) : [];
            } catch (error) {
                return [];
            }
        },

        setFavoriteIds: function (ids) {
            try {
                window.localStorage.setItem(this.favoritesStorageKey, JSON.stringify(ids));
            } catch (error) {
                return;
            }
        },

        toggleFavoriteState: function (productId) {
            var ids = this.getFavoriteIds();
            var exists = ids.indexOf(productId) !== -1;
            if (exists) {
                ids = ids.filter(function (id) {
                    return id !== productId;
                });
            } else {
                ids.push(productId);
            }
            this.setFavoriteIds(ids);
            return !exists;
        },

        syncFavoriteButtons: function () {
            var isFavorite = this.getFavoriteIds().indexOf(this.productId) !== -1;
            this.renderFavoriteState(isFavorite);
        },

        renderFavoriteState: function (isFavorite) {
            $(".js-detail-favorite").each(function () {
                var $button = $(this);
                var $icon = $button.find("i");
                $button.attr("aria-pressed", isFavorite ? "true" : "false");
                $button.toggleClass("btn-danger", isFavorite);
                $button.toggleClass("btn-outline-danger", !isFavorite);
                $icon.removeClass("bi-heart bi-heart-fill").addClass(isFavorite ? "bi-heart-fill" : "bi-heart");
                if ($button.text().trim().length > 0) {
                    $button.contents().filter(function () {
                        return this.nodeType === 3;
                    }).last().replaceWith(isFavorite ? " Retirer des favoris" : " Ajouter aux favoris");
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
