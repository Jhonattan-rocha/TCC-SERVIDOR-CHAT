from flask import request, jsonify
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from Model.tables import *

modules = {
    'CHAT': Chat,
    'USER': User,
    'Mensagem': Mensagem,
    'Arquivo': Arquivo
}

def create_condition(column, operator, value):
    if operator == 'eq':
        return column == value
    elif operator == 'ne':
        return column != value
    elif operator == 'lt':
        return column < value
    elif operator == 'not':
        return column != value
    elif operator == 'gt':
        return column > value
    elif operator == 'like':
        return column.like(f'%{value}%')
    else:
        return None

def handle_custom_filter(data):
    filter_param = request.args.get('filter')
    limit = request.args.get("limit")
    module = request.args.get("module")
    backrefs = request.args.get("include")

    if not module:
        return jsonify({
            'result': None,
            'error': 'Modulo alvo não informado'
        }), 404
    
    try:
        if not limit:
            limit = 100
        else:
            limit = int(limit)
    except Exception as e:
        return jsonify({
            'result': None,
            'error': 'Limite inválido'
        }), 400


    if filter_param:
        query = str(filter_param).split('+')

        if len(query) < 3:
            return jsonify({
                'result': None,
                'error': 'Query passada está errada'
            }), 405

        if len(query) == 3:
            attribute = query[0]
            operator = query[1]
            value = query[2]
            
            filtered_data = []

            if operator == 'eq':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute) == value).limit(limit)
            elif operator == 'ne':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute) != value).limit(limit)
            elif operator == 'lt':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute) < value).limit(limit)
            elif operator == 'not':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute) != value).limit(limit)
            elif operator == 'gt':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute) > value).limit(limit)
            elif operator == 'like':
                filtered_data = modules[module].query.filter(getattr(modules[module], attribute).like(f'%{value}%')).limit(limit)
            
            for backref in backrefs:
                query = query.options(joinedload(backref))
            
            filtered_data = filtered_data.all()
            
            return jsonify({
                'result': [item.__dict__ for item in filtered_data],
                'error': None
            }), 200
                
        if len(query) == 5:
            attribute = query[0]
            operator = query[1]
            value1 = query[2]
            logic_operator = query[3]
            value2 = query[4]

            # Verifica se o atributo existe no modelo
            if hasattr(modules[module], attribute):
                attribute_column = getattr(modules[module], attribute)

                if operator in ['eq', 'ne', 'lt', 'not', 'gt', 'like']:
                    # Aplica a primeira condição
                    condition1 = create_condition(attribute_column, operator, value1)

                    if logic_operator == 'or':
                        # Aplica a lógica OR com a segunda condição
                        condition2 = create_condition(attribute_column, operator, value2)
                        filtered_data = modules[module].query.filter(or_(condition1, condition2)).limit(limit)
                        
                        for backref in backrefs:
                            query = query.options(joinedload(backref))
            
                        filtered_data = filtered_data.all()
                        return jsonify({
                            'result': [item.__dict__ for item in filtered_data],
                            'error': None
                        }), 200
                    elif logic_operator == 'and':
                        # Aplica a lógica AND com a segunda condição
                        condition2 = create_condition(attribute_column, operator, value2)
                        filtered_data = modules[module].query.filter(and_(condition1, condition2)).limit(limit)
                        
                        for backref in backrefs:
                            query = query.options(joinedload(backref))
            
                        filtered_data = filtered_data.all()
                        
                        return jsonify({
                            'result': [item.__dict__ for item in filtered_data],
                            'error': None
                        }), 200

        
        if len(query) == 7:
            filters = []

            for i in range(0, len(query), 3):
                attribute = query[i]
                operator = query[i + 1]
                value = query[i + 2]

                if hasattr(modules[module], attribute):
                    attribute_column = getattr(modules[module], attribute)

                    condition = create_condition(attribute_column, operator, value)
                    if condition:
                        filters.append(condition)

            if len(filters) > 0:
                # Aplica as condições com o operador AND
                filtered_data = modules[module].query.filter(and_(*filters)).limit(limit)
                
                for backref in backrefs:
                    query = query.options(joinedload(backref))
    
                filtered_data = filtered_data.all()

                # Faça o processamento com os dados filtrados (filtered_data) como necessário
                return jsonify({
                    'result': [item.__dict__ for item in filtered_data],
                    'error': None
                }), 200
