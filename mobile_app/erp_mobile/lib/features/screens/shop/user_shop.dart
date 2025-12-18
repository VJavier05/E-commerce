import 'package:flutter/material.dart';
import 'package:shewear/common/widgets/appbar/appbar.dart';
import 'package:shewear/common/widgets/appbar/tabbar.dart';
import 'package:shewear/common/widgets/containers/search_container.dart';
import 'package:shewear/common/widgets/shop_products/category_tab.dart';
import 'package:shewear/features/screens/home/user_home.dart';
import 'package:shewear/utils/constants/colors.dart';
import 'package:shewear/utils/constants/sizes.dart';
import 'package:shewear/utils/helpers/helper_functions.dart';
import 'package:shewear/features/screens/cart/addtocart.dart';

class UserStore extends StatelessWidget {
  const UserStore({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 9,
      child: Scaffold(
        appBar: JAppBar(
          title: Text("Store"),
          actions: [
            JCountCounterIcon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const AddToCart()),
                );
              },
              iconColor: JColors.black,
            ),
          ],
        ),
        body: NestedScrollView(
            headerSliverBuilder: (_, innerBoxIsScrolled) {
              return [
                SliverAppBar(
                    automaticallyImplyLeading: false,
                    pinned: true,
                    floating: true,
                    backgroundColor: JHelperFunctions.isDarkMode(context)
                        ? JColors.black
                        : JColors.white,
                    expandedHeight: 150, // Adjust height based on design
                    flexibleSpace: FlexibleSpaceBar(
                      background: Padding(
                        padding: EdgeInsets.all(JSizes.defaultSpace),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(height: JSizes.spaceBtwItems),
                            JSearchContainer(
                              hintText: "Search for products...",
                              showBackground: false,
                              padding: EdgeInsets.zero,
                              onChanged: (query) {
                                print("User searched: $query");
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                    bottom: JTabBar(tabs: [
                      Tab(child: Text("All")),
                      Tab(child: Text("Dress")),
                      Tab(child: Text("Blouse")),
                      Tab(child: Text("Activewear")),
                      Tab(child: Text("Lingerie")),
                      Tab(child: Text("Jackets")),
                      Tab(child: Text("Coats")),
                      Tab(child: Text("Shoes")),
                      Tab(child: Text("Accessories")),
                    ]))
              ];
            },
            body: TabBarView(
              children: [
                JCategorytab(
                  title: "All Products",
                ),
                JCategorytab(
                  title: "Dress",
                ),
                JCategorytab(
                  title: "Blouses",
                ),
                JCategorytab(
                  title: "Activewears",
                ),
                JCategorytab(
                  title: "Lingeries",
                ),
                JCategorytab(
                  title: "Jackets",
                ),
                JCategorytab(
                  title: "Coats",
                ),
                JCategorytab(
                  title: "Shoes",
                ),
                JCategorytab(
                  title: "Accessories",
                ),
              ],
            ) // Add TabBarView content here
            ),
      ),
    );
  }
}
