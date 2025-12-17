import pandas as pd
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from django.views import View

import plotly.express as px
import plotly.graph_objects as go

from math import pi
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, Slider, CustomJS
from bokeh.transform import cumsum
from bokeh.palettes import Spectral6, Category20c
from bokeh.resources import CDN
import decimal
from bokeh.layouts import column

from main.repositories.statsrepository import StatsRepository

from main.repositories.repomanager import RepositoryManager
from rest_framework import viewsets, status
from .serializers import *
from rest_framework.permissions import IsAuthenticated

repo = RepositoryManager()

class TrainViewSet(viewsets.ModelViewSet):
	queryset = repo.trains.get_all()
	serializer_class = TrainSerializer

class PassengerViewSet(viewsets.ModelViewSet):
	queryset = repo.passengers.get_all()
	serializer_class = PassengerSerializer

class TicketViewSet(viewsets.ModelViewSet):
	queryset = repo.tickets.get_all()
	serializer_class = TicketSerializer
	

class TicketReport(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tickets = repo.tickets.get_all()
        total_tickets = tickets.count() 
        total_money = sum(ticket.price for ticket in tickets)

        report = {
            "total_tickets": total_tickets,
            "total_income": total_money,
            "average_price": total_money / total_tickets if total_tickets else 0
        }

        return Response(report, status=status.HTTP_200_OK)
	
class BasePandasView(APIView):
    
    def analyze_dataframe(self, df, value_col):
        if df.empty:
            return {}
        
        mean_val = df[value_col].mean()
        median_val = df[value_col].median()
        min_val = df[value_col].min()
        max_val = df[value_col].max()

        def safe_json(val):
            return 0 if pd.isna(val) or np.isinf(val) else val

        stats = {
            "statistics": {
                "mean": safe_json(mean_val),
                "median": safe_json(median_val),
                "min": safe_json(min_val),
                "max": safe_json(max_val),
            }
        }
        return stats

    # аналітика для поїздів по квитках
class TrainRevenueAnalyticsView(BasePandasView):
    def get(self, request):
        queryset = StatsRepository.get_trains_by_revenue()
        
        data = list(queryset.values('train_number', 'total_revenue', 'tickets_sold'))
        df = pd.DataFrame(data)       
        

        if df.empty:
            return Response({"message": "No data available"})

        df['total_revenue'] = df['total_revenue'].fillna(0.0).astype(float)
        df['tickets_sold'] = df['tickets_sold'].fillna(0).astype(int)

        response_data = self.analyze_dataframe(df, 'total_revenue')

        df['load_category'] = pd.cut(
            df['tickets_sold'], 
            bins=[0, 10, 20, 30], 
            labels=['Low', 'Medium', 'High'], 
            include_lowest=True
        )

        
        df['load_category'] = df['load_category'].astype(object) 

        grouped = df.groupby('load_category', observed=False)['total_revenue'].sum().reset_index()
        
        grouped['load_category'] = grouped['load_category'].astype(object)

        response_data['grouped_analysis'] = grouped.to_dict(orient='records')
        response_data['raw_data'] = df.to_dict(orient='records')

        return Response(response_data)

    # ціна для шляху
class RoutePriceAnalyticsView(BasePandasView):
    """
    URI: /api/analytics/routes/
    Аналіз цін по маршрутах.
    """
    def get(self, request):

        queryset = StatsRepository.get_avg_price_per_route()
        
        df = pd.DataFrame(list(queryset))
        
        if df.empty:
            return Response({"message": "No data available"})
            
        df['avg_price'] = df['avg_price'].astype(float)

        response_data = self.analyze_dataframe(df, 'avg_price')
        
        response_data['statistics_for_route'] = df.to_dict(orient='records')
        
        return Response(response_data)
    
    # квитки в поїзді які є
class TrainTicketTypesAnalyticsView(BasePandasView):
    """
    URI: /api/analytics/train-classes/
    Аналіз класів вагонів
    """
    def get(self, request):
        queryset = StatsRepository.get_ticket_types_per_train()
        
        data = list(queryset.values(
            'train_number', 'plazkart_count', 'kupe_count', 'lux_count'
        ))
        df = pd.DataFrame(data)

        if df.empty:
            return Response({"message": "No data available"})

  
        df['dominant_class'] = df[['plazkart_count', 'kupe_count', 'lux_count']].idxmax(axis=1)

        df['total_seats'] = df['plazkart_count'] + df['kupe_count'] + df['lux_count']

        response_data = self.analyze_dataframe(df, 'total_seats')
        
        dominance_stats = df['dominant_class'].value_counts().reset_index()
        dominance_stats.columns = ['ticket_type', 'train_count']
        
        rozpodil = df[['plazkart_count', 'kupe_count', 'lux_count']].sum()

        response_data["total_for_class"] = rozpodil.to_dict()
        response_data['class_dominance'] = dominance_stats.to_dict(orient='records')
        response_data['raw_data'] = df.to_dict(orient='records')

        return Response(response_data)


# топ за витратами
class TopSpendersAnalyticsView(BasePandasView):
    """
    URI: /api/analytics/passengers/top-spenders/
    Аналіз найбільш катаються.
    """
    def get(self, request):
        # ?min_spent=n
        min_spent = request.query_params.get('min_spent', 1000)
        queryset = StatsRepository.get_top_spending_passengers(min_spent=int(min_spent))
        
        data = list(queryset.values('first_name', 'last_name', 'total_spent', 'trips_count'))
        df = pd.DataFrame(data)

        if df.empty:
            return Response({"message": "No qualifying passengers found"})

        df['total_spent'] = df['total_spent'].astype(float)

        response_data = self.analyze_dataframe(df, 'total_spent')

        df['avg_check'] = df['total_spent'] / df['trips_count']

        
        response_data['top_list'] = df.head(10).to_dict(orient='records')

        return Response(response_data)


# пільговики
class SocialStatsAnalyticsView(BasePandasView):
    """
    URI: /api/analytics/trains/social-stats/
    Аналіз пільг.
    """
    def get(self, request):
        queryset = StatsRepository.get_social_stats_by_train()
        
        data = list(queryset.values('train_number', 'military_count', 'student_count', 'total_passengers'))
        df = pd.DataFrame(data)

        if df.empty:
            return Response({"message": "No data available"})

        df['social_percentage'] = ((df['military_count'] + df['student_count']) / df['total_passengers'] * 100).round(2)

        response_data = self.analyze_dataframe(df, 'social_percentage') 

        max_student_train = df.loc[df['student_count'].idxmax()]
        
        response_data['insight'] = {
            "most_student_train": max_student_train['train_number'],
            "student_count": int(max_student_train['student_count'])
        }
        response_data['raw_data'] = df.to_dict(orient='records')

        return Response(response_data)

    # люкси
class LuxuryOnlyAnalyticsView(BasePandasView):
    """
    URI: /api/analytics/passengers/luxury-only/
    Аналіз лакшері.
    """
    def get(self, request):
        queryset = StatsRepository.get_luxury_only_passengers()
        
        data = list(queryset.values('first_name', 'last_name', 'lux_tickets'))
        df = pd.DataFrame(data)

        if df.empty:
            return Response({"message": "No luxury-only passengers found"})

        response_data = self.analyze_dataframe(df, 'lux_tickets')

        df['loyalty'] = df['lux_tickets'].apply(lambda x: 'One-time' if x == 1 else 'Regular')
        loyalty_stats = df['loyalty'].value_counts().reset_index().to_dict(orient='records')

        response_data['loyalty_analysis'] = loyalty_stats
        response_data['passengers'] = df.to_dict(orient='records')

        return Response(response_data)




class DashboardPlotlyView(View):
    def get(self, request):
        search_query = request.GET.get('search_query', '')
        city_filter = request.GET.get('city_filter', '')
        try:
            min_revenue = int(request.GET.get('min_revenue', 0))
        except (ValueError, TypeError):
            min_revenue = 0

        def get_empty_fig(title_text):
            fig = go.Figure()
            fig.update_layout(
                title=title_text,
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[{
                    "text": "Немає даних",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 20}
                }]
            )
            return fig

        available_cities = StatsRepository.get_all_departure_cities()
        
        q1 = StatsRepository.get_trains_by_revenue()
        df1 = pd.DataFrame(list(q1.values('train_number', 'total_revenue')))
        if not df1.empty:
            df1['total_revenue'] = df1['total_revenue'].fillna(0).astype(float)
            df1 = df1[df1['total_revenue'] >= min_revenue]

        q2 = StatsRepository.get_top_spending_passengers(min_spent=0)
        df2 = pd.DataFrame(list(q2.values('last_name', 'total_spent')))
        if not df2.empty:
            df2['last_name'] = df2['last_name'].fillna('Unknown').astype(str)
            if search_query:
                df2 = df2[df2['last_name'].str.contains(search_query, case=False)]

        q3 = StatsRepository.get_ticket_types_per_train()
        df3 = pd.DataFrame(list(q3.values('train_number', 'plazkart_count', 'kupe_count', 'lux_count')))
        
        q4 = StatsRepository.get_avg_price_per_route()
        df4 = pd.DataFrame(list(q4))
        if not df4.empty:
            df4['train__begin_point'] = df4['train__begin_point'].fillna('Unknown')
            df4['train__end_point'] = df4['train__end_point'].fillna('Unknown')
            df4['train__begin_point'] = df4['train__begin_point'].astype(str)
            df4['train__end_point'] = df4['train__end_point'].astype(str)

            df4['route'] = df4['train__begin_point'] + ' -> ' + df4['train__end_point']
            
            if city_filter:
                df4 = df4[df4['train__begin_point'] == city_filter]

        q5 = StatsRepository.get_social_stats_by_train()
        df5 = pd.DataFrame(list(q5.values('student_count', 'military_count')))

        q6 = StatsRepository.get_luxury_only_passengers()
        df6 = pd.DataFrame(list(q6.values('lux_tickets')))


        if not df1.empty:
            fig1 = px.bar(df1, x='train_number', y='total_revenue', title=f"Дохід > {min_revenue}")
        else:
            fig1 = get_empty_fig("Дохід (Немає даних)")
        
        if not df2.empty:
            fig2 = px.bar(df2.head(10), x='last_name', y='total_spent', title="Топ пасажири")
        else:
            fig2 = get_empty_fig("Топ пасажири (Немає даних)")
        
        if not df3.empty:
            df3_m = df3.melt(id_vars='train_number', value_vars=['plazkart_count', 'kupe_count', 'lux_count'])
            fig3 = px.bar(df3_m, x='train_number', y='value', color='variable', barmode='group', title="Типи вагонів")
        else:
            fig3 = get_empty_fig("Типи вагонів (Немає даних)")

        if not df4.empty:
            fig4 = px.bar(df4, x='route', y='avg_price', title=f"4. Маршрути ({city_filter or 'Всі'})",
                          labels={'avg_price': 'Середня ціна (грн)', 'route': 'Маршрут'})
        else:
            fig4 = get_empty_fig("4. Маршрути")

        if not df5.empty and (df5['student_count'].sum() + df5['military_count'].sum() > 0):
            fig5 = px.pie(names=['Student', 'Military'], values=[df5['student_count'].sum(), df5['military_count'].sum()], title="Пільговики")
        else:
            fig5 = get_empty_fig("Пільговики (Немає даних)")

        if not df6.empty and 'lux_tickets' in df6.columns:
            fig6 = px.histogram(df6, x='lux_tickets', title="Люкс-клієнти")
        else:
            fig6 = get_empty_fig("Люкс-клієнти (Немає даних)")

        context = {
            'plot1': fig1.to_html(full_html=False), 'plot2': fig2.to_html(full_html=False),
            'plot3': fig3.to_html(full_html=False), 'plot4': fig4.to_html(full_html=False),
            'plot5': fig5.to_html(full_html=False), 'plot6': fig6.to_html(full_html=False),
            'current_search': search_query, 'current_city': city_filter, 'current_min_rev': min_revenue, 'cities': available_cities
        }
        return render(request, 'analytics/dashboard_plotly.html', context)


#bokeh
class DashboardBokehView(View):
    def get(self, request):
        
        layouts = {}

        def empty_plot(title):
            p = figure(title=title, height=400, width=600)
            p.text(x=0, y=0, text=["Немає даних"], text_align="center")
            p.xaxis.visible = False
            p.yaxis.visible = False
            return p


        q1 = StatsRepository.get_trains_by_revenue()

        df1 = pd.DataFrame([{
            'train_number': str(train.train_number),
            'total_revenue': float(train.total_revenue or 0)
        } for train in q1])

        if not df1.empty:
            source1 = ColumnDataSource(df1)
            original1 = ColumnDataSource(df1.copy())

            p1 = figure(
                x_range=df1['train_number'].tolist(), height=400, title="1. Дохід потягів", tools="")
            p1.vbar( x='train_number', top='total_revenue', width=0.8, source=source1, color="#718dbf")
            p1.yaxis.axis_label = "Грн"

            slider1 = Slider(start=0,end=df1['total_revenue'].max(),value=0,step=100,title="Мін. дохід")

            slider1.js_on_change("value", CustomJS(
                args=dict(s=source1, o=original1, sl=slider1),
                code="""
                    const data = s.data;
                    const orig = o.data;
                    const thr = sl.value;
                    for (let i = 0; i < orig['total_revenue'].length; i++) {
                        data['total_revenue'][i] = orig['total_revenue'][i] >= thr ? orig['total_revenue'][i] : 0;
                    }
                    s.change.emit();
                """
            ))

            layouts['plot1'] = column(slider1, p1)
        else:
            layouts['plot1'] = empty_plot("1. Дохід")


        q2 = StatsRepository.get_top_spending_passengers(min_spent=0)
        data2 = []
        for item in q2:
            lname = getattr(item, 'last_name', None)
            if lname is None and isinstance(item, dict): lname = item.get('last_name', 'Unknown')
            spent = getattr(item, 'total_spent', 0)
            if spent is None and isinstance(item, dict): spent = item.get('total_spent')
            data2.append({
                'last_name': str(lname),
                'total_spent': float(spent or 0)
            })
        df2 = pd.DataFrame(data2).head(10)

        if not df2.empty:
            if df2['last_name'].duplicated().any():
                df2['last_name'] = [f"{n} ({i})" for i, n in enumerate(df2['last_name'])]

            source2 = ColumnDataSource(df2)

            p2 = figure(x_range=df2['last_name'].tolist(), height=400, title="2. Топ пасажири")
            p2.scatter(x='last_name', y='total_spent', size=15, color="orange", source=source2)

            layouts['plot2'] = p2 
        else:
            layouts['plot2'] = empty_plot("2. Топ пасажири")


        q3 = StatsRepository.get_ticket_types_per_train()
        data3 = []
        for item in q3:
            t_num = getattr(item, 'train_number', None)
            if t_num is None and isinstance(item, dict): t_num = item.get('train_number')
            pl = getattr(item, 'plazkart_count', 0) or 0
            kp = getattr(item, 'kupe_count', 0) or 0
            lx = getattr(item, 'lux_count', 0) or 0
            if isinstance(item, dict):
                pl = item.get('plazkart_count', 0)
                kp = item.get('kupe_count', 0)
                lx = item.get('lux_count', 0)

            data3.append({
                'train_number': str(t_num),
                'plazkart_count': float(pl),
                'kupe_count': float(kp),
                'lux_count': float(lx),
            })
        df3 = pd.DataFrame(data3)
        
        if not df3.empty:
            cols_types = ['plazkart_count', 'kupe_count', 'lux_count']
            df3['total'] = df3[cols_types].sum(axis=1)

            source3 = ColumnDataSource(df3)
            original3 = ColumnDataSource(df3.copy())
            p3 = figure(x_range=df3['train_number'].tolist(), height=400, title="3. Типи вагонів")
            p3.vbar_stack(cols_types, x='train_number', width=0.8, color=Spectral6[:3], source=source3,
                        fill_alpha='alpha') 

            slider3 = Slider(start=0, end=df3['total'].max(), value=0, step=1, title="Мін. місць")
            source3.data['total'] = df3['total'].values

            slider3.js_on_change("value", CustomJS(args=dict(s=source3,o=original3, sl=slider3), code="""
                const data = s.data;
                const thr = sl.value;
                const orig = o.data;
                                                   
                for (let i = 0; i < data['total'].length; i++) {
                    data['alpha'][i] = (orig['total'][i] >= thr) ? orig['total'][i] : 0;
                }
                s.change.emit();
            """))
            layouts['plot3'] = column(slider3, p3)
        else:
            layouts['plot3'] = empty_plot("3. Типи вагонів")


        q4 = StatsRepository.get_avg_price_per_route()
        data4 = []
        for item in q4:
            start = item.get('train__begin_point', '?')
            end = item.get('train__end_point', '?')
            price = float(item.get('avg_price') or 0) 
            data4.append({
                'route': f"{start} - {end}",
                'avg_price': price
            })
        df4 = pd.DataFrame(data4)

        if not df4.empty:
            source4 = ColumnDataSource(df4)
            original4 = ColumnDataSource(df4.copy())

            p4 = figure(x_range=df4['route'].tolist(), height=500, width=800, title="4. Середня ціна маршруту", tools="")
            p4.vbar(x='route', top='avg_price', width=0.5, source=source4, color="#2b8cbe")
            p4.yaxis.axis_label = "Ціна (грн)"

            slider4 = Slider(start=0, end=df4['avg_price'].max(), value=0, step=10, title="Мін. ціна")
            slider4.js_on_change("value", CustomJS(args=dict(s=source4, o=original4, sl=slider4), code="""
                const data = s.data;
                const orig = o.data;
                const thr = sl.value;
                for (let i = 0; i < orig['avg_price'].length; i++) {
                    if (orig['avg_price'][i] >= thr) {
                         data['avg_price'][i] = orig['avg_price'][i];
                    } else {
                         data['avg_price'][i] = 0;
                    }
                }
                s.change.emit();
            """))
            layouts['plot4'] = column(slider4, p4)
        else:
            layouts['plot4'] = empty_plot("4. Маршрути")


        q5 = StatsRepository.get_social_stats_by_train()
        data5 = []
        for item in q5:
            st = getattr(item, 'student_count', 0)
            if st is None and isinstance(item, dict): st = item.get('student_count', 0)
            mil = getattr(item, 'military_count', 0)
            if mil is None and isinstance(item, dict): mil = item.get('military_count', 0)
            data5.append({
                'student_count': float(st or 0),
                'military_count': float(mil or 0)
            })
        df5 = pd.DataFrame(data5)

        s_sum = df5['student_count'].sum() if not df5.empty else 0.0
        m_sum = df5['military_count'].sum() if not df5.empty else 0.0

        if (s_sum + m_sum) > 0:
            data_pie = pd.DataFrame({
                'category': ['Students', 'Military'],
                'value': [s_sum, m_sum]
            })
            data_pie['angle'] = data_pie['value'] / data_pie['value'].sum() * 2 * pi
            data_pie['color'] = Category20c[3][:2]
            
            source5 = ColumnDataSource(data_pie)
            
            p5 = figure(height=400, title="5. Пільговики", toolbar_location=None, tools="hover", tooltips="@category: @value")
            p5.wedge(x=0, y=1, radius=0.4, 
                     start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                     line_color="white", fill_color='color', legend_field='category', source=source5)
            p5.axis.visible = False
            p5.grid.grid_line_color = None

            layouts['plot5'] = p5
        else:
            layouts['plot5'] = empty_plot("5. Пільговики")


        q6 = StatsRepository.get_luxury_only_passengers()
        data6 = []
        for item in q6:
            lname = getattr(item, 'last_name', None)
            if lname is None and isinstance(item, dict): lname = item.get('last_name', 'Unknown')

            lux = getattr(item, 'lux_tickets', 0)
            if lux is None and isinstance(item, dict): lux = item.get('lux_tickets', 0)

            data6.append({
                'last_name': str(lname),
                'lux_tickets': float(lux or 0)
            })
        df6 = pd.DataFrame(data6)

        if not df6.empty:
            df6 = df6.sort_values('lux_tickets', ascending=False).head(10)
            
            if df6['last_name'].duplicated().any():
                df6['last_name'] = [f"{n} ({i})" for i, n in enumerate(df6['last_name'])]
            
            source6 = ColumnDataSource(df6)
            
            p6 = figure(x_range=df6['last_name'].tolist(), height=400, title="6. Топ клієнти Люкс")
            
            p6.vbar(x='last_name', top='lux_tickets', width=0.5, source=source6, color="green")
            
            
            p6.yaxis.axis_label = "Кількість поїздок"

            layouts['plot6'] = p6
        else:
            layouts['plot6'] = empty_plot("6. Топ клієнти Люкс")


        script, divs = components(layouts)
        js_resources = CDN.render()

        return render(request, 'analytics/bokeh_dashboard_single.html', {
            'script': script,
            'divs': divs,
            'js_resources': js_resources
        })