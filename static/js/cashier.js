/**
 * Created by lujianxing on 2014/11/6.
 * kevinlu1010@qq.com
 */

//分页构建函数
//total_page int ：总的页数
//now_page int : 当前页数
//返回分页的html代码
function page_builder(total_page, now_page) {
    tmp = "";
    one_page = "<li class=''><a href='#n'>1</a></li>";
    last_page = "<li class=''><a href='#n'>" + total_page + "</a></li>";
    omit_page = "<li class='disabled'><a href='#n'>…</a></li>";
    if (total_page < 11) {
        for (var i = 1; i < total_page + 1; i++) {
            if (now_page == i) {
                tmp += "<li class='active'><a >" + i + "</a></li>";

            } else {
                tmp += "<li class=''><a href='#n'>" + i + "</a></li>";
            }
        }
    } else if (now_page < 5) {
        for (var i = 1; i < 10 + 1; i++) {
            if (now_page == i) {
                tmp += "<li class='active'><a href='#n'>" + i + "</a></li>";

            } else {
                tmp += "<li class=''><a href='#n'>" + i + "</a></li>";
            }

        }
        tmp = tmp + omit_page + last_page;
    } else {
        end_page = now_page + 6;
        if (end_page > total_page + 1)
            end_page = total_page + 1;
        tmp += one_page + omit_page
        for (var i = now_page - 4; i < end_page; i++) {
            if (now_page == i) {
                tmp += "<li class='active'><a href='#n'>" + i + "</a></li>";

            } else {
                tmp += "<li class=''><a href='#n'>" + i + "</a></li>";
            }
        }
        if (end_page < total_page)
            tmp += omit_page + last_page;

    }
    return tmp;
}
