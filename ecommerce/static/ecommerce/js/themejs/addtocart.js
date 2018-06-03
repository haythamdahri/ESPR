	// Cart add remove functions
	var cart = {
		'add': function(id_product, logged, product_name, image, url_product) {
		    if(logged === "True") {
		        var form = $('#formAddCart'+id_product);
                $.ajax({
                    url: form.attr("data-validate-url"),
                    data: form.serialize(),
                    dataType: 'json',
                    success: function (data) {
                        if(data.message_error === ""){
                            addProductNotice('Product added to Cart', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3><a href="' + url_product + '">"' + product_name + '"</a> added to <a href="/e_commerce/cart">shopping cart</a>!</h3>', 'success');
                            var html = '<td class="text-center">' +
                                '<a href="' + url_product + '"><img src="' + image + '" style="width:70px;" alt="image ' + product_name + '" title="' + product_name + '" class="preview"></a></td>';
                            html += '<td class="text-left"><a class="cart_product_name" href="' + url_product + '">' + product_name + '</a></td>';
                            html += '<td class="text-center">x' + data.quantity + '</td>';
                            var price = "";
                            if(data.price !== "")
                                price = data.price.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
                            html += '<td class="text-right">'+price+' Dh</td>';
                            html += '<td class="text-right"><a href="#" class="fa fa-edit"></a></td>';
                            html += '<td class="text-right">';
                            html += '<form id="formRemoveFromCart'+ id_product +'" method="get" action="/e_commerce/cart/remove_from_cart" data-validate-url="/e_commerce/cart/remove_from_cart/">';
                            html += '<input type="hidden" name="product" value="' + id_product + '">';
                            html += '<input type="hidden" name="color" value="'+data.color_id+'"></form>';
                            html += '<a href="javascript:" onclick="cart.remove(\'' + id_product + '\', \'' + product_name + '\', \'' + image + '\', \'' + url_product + '\');" class="fa fa-times fa-delete"></a></td>';
                            //html += '<td class="text-right"><form><a href="#" class="fa fa-times fa-delete"></a></form></td>';
                            var tr = document.createElement("tr");
                            var id = "line" + id_product;
                            //tr.id = id;
                            tr.setAttribute("id", id);
                            tr.innerHTML = html;
                            document.getElementById("table_cart").appendChild(tr);
                            $("#total_cart_1").text("$" + data.total_price_in_cart.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "");
                            $("#total_cart_2").text("$" + data.total_price_in_cart.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "");
                            $("#number_in_cart").text(data.number_products_in_cart);
                            if(data.message_warning !== "")
                                addProductNotice('Ajouter ' + product_name + ' au Chariot', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3>' + data.message_warning + '</h3>', 'success');
                        }
                        else
                        {
                            addProductNotice('Ajouter ' + product_name + ' au Chariot', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3>' + data.message_error + '</h3>', 'success');
                        }
                    }
                });
            }
            else
            {
                addProductNotice('Ajouter produit au Chariot', '<img src="' + image + '" alt="">', '<h3>Vous devez <a href="/main/login">Se Connecter</a>  pour pouvoir sauvegarder <a href="' + url_product + '">"' + product_name + '"</a> dans votre <a href="/e_commerce/cart">Chariot</a>!</h3>', 'success');
            }
		},
		'remove':function(id_product, product_name, image, url_product) {
		    var form = $('#formRemoveFromCart'+id_product);
            $.ajax({
                url: form.attr("data-validate-url"),
                data: form.serialize(),
                dataType: 'json',
                success: function (data) {
                    if(data.message_error === ""){
                        addProductNotice('Product removed from Cart', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3><a href="' + url_product + '">"' + product_name + '"</a> removed from <a href="/e_commerce/cart">shopping cart</a>!</h3>', 'success');
                        var tr = $('#line' + id_product);
                        tr.hide();
                        $("#total_cart_1").text("$" + data.total_price_in_cart.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "");
                        $("#total_cart_2").text("$" + data.total_price_in_cart.toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") + "");
                        $("#number_in_cart").text(data.number_products_in_cart);
                    }
                    else
                    {
                        addProductNotice('Retirer ' + product_name + ' depuis votre Chariot', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3>' + data.message_error + '</h3>', 'success');
                    }
                }
            });
        }
	};

	var wishlist = {
	    'add': function(id_product, logged, product_name, image, url_product) {
		    if(logged === "True") {
		        var form = $('#formAddWish'+id_product);
                $.ajax({
                    url: form.attr("data-validate-url"),
                    data: form.serialize(),
                    dataType: 'json',
                    success: function (data) {
                        if(data.message_error === ""){
                            addProductNotice('Product added to Wish list', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3><a href="' + url_product + '">"' + product_name + '"</a> added to <a href="/e_commerce/wish_list">wish list</a>!</h3>', 'success');
                            $("#number_in_wish_list").text("Wish List (" + data.number_products_in_wish_list + ")");
                        }
                        else
                        {
                            addProductNotice('Add ' + product_name + ' to Wish list', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3>' + data.message_error + '</h3>', 'success');
                        }
                    }
                });
            }
            else
            {
                addProductNotice('Add product to Wish list', '<img src="' + image + '" alt="">', '<h3>You must <a href="#">login</a>  to save <a href="' + url_product + '">"' + product_name + '"</a> to your <a href="/e_commerce/wish_list">wish list</a>!</h3>', 'success');
            }
		}
	};
	var compare = {
	    'add': function(id_product, logged, product_name, image, url_product) {
		    if(logged === "True") {
		        var form = $('#formAddCompare'+id_product);
                $.ajax({
                    url: form.attr("data-validate-url"),
                    data: form.serialize(),
                    dataType: 'json',
                    success: function (data) {
                        if(data.message_error === ""){
                            addProductNotice('Produit ajouter à la Comparaison', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3><a href="' + url_product + '">"' + product_name + '"</a> ajouter à <a href="/e_commerce/compare">comparaison</a>!</h3>', 'success');
                            $("#number_in_compare").html("<i class='fa fa-refresh'></i>Compare (" + data.number_products_in_compare + ")");
                        }
                        else
                        {
                            addProductNotice('Ajouter ' + product_name + ' à comparaison', '<a href="' + url_product + '"><img src="' + image + '" alt=""></a>', '<h3>' + data.message_error + '</h3>', 'success');
                        }
                    }
                });
            }
            else
            {
                addProductNotice('Ajouter produit à comparaison', '<img src="' + image + '" alt="">', '<h3>Vous devez<a href="/main/login"> Se Connecter</a> pour pouvoir sauvegarder <a href="' + url_product + '">"' + product_name + '"</a> à votre <a href="/e_commerce/wish_list"> comparaison</a>!</h3>', 'success');
            }
		}
	};

	function addProductNotice(title, thumb, text, type) {
		$.jGrowl.defaults.closer = false;
		//Stop jGrowl
		//$.jGrowl.defaults.sticky = true;
		var tpl = thumb + '<h3>'+text+'</h3>';
		$.jGrowl(tpl, {		
			life: 4000,
			header: title,
			speed: 'slow',
			theme: type
		});
	}