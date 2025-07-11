# Endpoints Públicos - Smart CAA API

## 📋 Resumo

O sistema Smart CAA possui alguns endpoints **públicos** (que não requerem autenticação) para permitir o cadastro inicial de pacientes e cuidadores.

## 🔓 Endpoints Públicos

### 1. Cadastro de Paciente
```http
POST /api/patients/
```

**Descrição**: Permite cadastrar um novo paciente sem necessidade de autenticação.

**Dados obrigatórios**:
- `name`: Nome completo
- `cpf`: CPF (com ou sem formatação)
- `email`: E-mail válido
- `phone`: Telefone
- `password`: Senha (mínimo 8 caracteres)

**Dados opcionais**:
- `cid`: Código CID
- `colors`: Cores preferidas
- `sounds`: Sons preferidos
- `smells`: Cheiros preferidos
- `hobbies`: Hobbies
- Dados de endereço (CEP, cidade, etc.)

**Exemplo**:
```json
{
    "name": "João Silva",
    "cpf": "12345678901",
    "email": "joao@teste.com",
    "phone": "(11) 99999-9999",
    "password": "senhaSegura123",
    "cid": "F84.0",
    "colors": "Azul, Verde",
    "sounds": "Música clássica"
}
```

### 2. Cadastro de Cuidador
```http
POST /api/caregivers/
```

**Descrição**: Permite cadastrar um novo cuidador sem necessidade de autenticação.

**Dados obrigatórios**:
- `name`: Nome completo
- `cpf`: CPF (com ou sem formatação)
- `email`: E-mail válido
- `phone`: Telefone
- `password`: Senha (mínimo 8 caracteres)

**Dados opcionais**:
- `profession`: Profissão
- Dados de endereço (CEP, cidade, etc.)

**Exemplo**:
```json
{
    "name": "Maria Santos",
    "cpf": "98765432109",
    "email": "maria@teste.com",
    "phone": "(11) 88888-8888",
    "password": "senhaSegura456",
    "profession": "Enfermeira"
}
```

## 🔒 Endpoints Protegidos

Todos os outros endpoints requerem autenticação via token JWT:

- `GET /api/patients/` - Listar pacientes
- `GET /api/caregivers/` - Listar cuidadores
- `GET /api/patients/{id}/` - Obter paciente específico
- `PUT/PATCH /api/patients/{id}/` - Atualizar paciente
- `DELETE /api/patients/{id}/` - Excluir paciente
- Todos os endpoints de relacionamentos
- Todos os endpoints de categorias e pictogramas

## 🔑 Processo de Autenticação

### 1. Cadastrar usuário (público)
```http
POST /api/patients/
```

### 2. Fazer login
```http
POST /authentication/token
{
    "username": "12345678901",  // CPF é o username
    "password": "senhaSegura123"
}
```

### 3. Usar token nas requisições
```http
GET /api/patients/
Authorization: Bearer {access_token}
```

## ⚙️ Funcionalidades Automáticas

### Criação Automática de Usuário

Quando um paciente ou cuidador é cadastrado:

1. **Username**: CPF (apenas números)
2. **Password**: Senha fornecida
3. **Email**: Email fornecido
4. **Nome**: `first_name` e `last_name` extraídos do nome completo

### Validações

1. **CPF**: Validação completa (formato + dígitos verificadores)
2. **Email**: Deve ser único no sistema
3. **Telefone**: Deve ser único no sistema
4. **Senha**: Seguir políticas de segurança do Django

### Tratamento de Duplicatas

- **CPF já existe**: Erro se já tem usuário associado
- **Email já existe**: Erro de validação
- **Telefone já existe**: Erro de validação

## 🧪 Exemplos de Teste

### Cadastro com Sucesso
```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "cpf": "12345678901",
    "email": "joao@teste.com",
    "phone": "(11) 99999-9999",
    "password": "senhaSegura123"
  }'
```

### Login Automático
```bash
curl -X POST http://localhost:8000/authentication/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "12345678901",
    "password": "senhaSegura123"
  }'
```

### Usar Token
```bash
curl -X GET http://localhost:8000/api/patients/ \
  -H "Authorization: Bearer {seu_access_token}"
```

## ⚠️ Considerações de Segurança

1. **Rate Limiting**: Considere implementar limite de requisições
2. **CAPTCHA**: Para evitar cadastros automatizados
3. **Validação de Email**: Implementar verificação de email
4. **Política de Senhas**: Senhas fortes obrigatórias
5. **Logs**: Monitorar tentativas de cadastro

## 📝 Códigos de Resposta

### Sucesso (201)
```json
{
    "id": 1,
    "name": "João Silva",
    "cpf": "123.456.789-01",
    "email": "joao@teste.com",
    "is_patient": true,
    "is_caregiver": false,
    "created_at": "2024-01-01T10:00:00Z"
}
```

### Erro de Validação (400)
```json
{
    "cpf": ["Esta pessoa já possui um usuário associado."],
    "email": ["Usuário com este E-mail já existe."]
}
```

### Erro de Autenticação (401) - Para endpoints protegidos
```json
{
    "detail": "As credenciais de autenticação não foram fornecidas."
}
```
