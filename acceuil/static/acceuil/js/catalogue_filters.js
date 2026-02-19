/* global jQuery */
(function ($) {
    "use strict";

    var catalogueModule = {
        init: function () {
            this.$form = $("#catalog-filter-form");
            this.$container = $("section[data-filter-url]");
            this.filterUrl = this.$container.data("filter-url");
            this.bindEvents();
            this.setupCsrfForAjax();
        },

        bindEvents: function () {
            this.$form.on("submit", this.handleFormSubmit.bind(this));
            this.$form.on("change", "select", this.handleAutoFilter.bind(this));
            $(document).on("click", ".js-category-link", this.handleCategoryClick.bind(this));
        },

        setupCsrfForAjax: function () {
            var csrfToken = this.getCookie("csrftoken");
            $.ajaxSetup({
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrfToken || "");
                }
            });
        },

        handleFormSubmit: function (event) {
            event.preventDefault();
            this.fetchAndRender();
        },

        handleAutoFilter: function () {
            this.fetchAndRender();
        },

        handleCategoryClick: function (event) {
            event.preventDefault();
            var slug = $(event.currentTarget).data("category-slug") || "";
            $("#catalog-category").val(slug);
            this.fetchAndRender();
        },

        fetchAndRender: function () {
            var self = this;
            $.ajax({
                url: this.filterUrl,
                method: "GET",
                data: this.$form.serialize(),
                success: function (response) {
                    $("#catalog-sidebar").html(response.sidebar_html);
                    $("#catalog-products").html(response.products_html);
                    $("#catalog-context-filters").html(response.context_filters_html);
                    $("#catalog-city").html(response.city_options_html);
                    $("#catalog-result-count").text(response.total_produits + " produits");
                },
                error: function () {
                    self.showTemporaryError();
                }
            });
        },

        showTemporaryError: function () {
            var html = "<div class='alert alert-danger mb-3'>Erreur de filtrage. Veuillez reessayer.</div>";
            this.$container.prepend(html);
            setTimeout(function () {
                $(".alert-danger").first().remove();
            }, 2500);
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
        if ($("#catalog-filter-form").length > 0) {
            catalogueModule.init();
        }
    });
})(jQuery);

