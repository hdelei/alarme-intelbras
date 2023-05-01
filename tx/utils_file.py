from watchdog.events import FileSystemEventHandler

class FileHandler(FileSystemEventHandler):
    new_event = False
    alarm_event = {}
    buffer = ''
    is_valid = False
    def __init__(self):
      with open('event_buffer.txt', 'w') as f:
        f.write('')

    
    def on_modified(self, event):        
      if event.event_type == 'modified' and event.src_path == 'event_buffer.txt':                 
        self.buffer = self.get_buffer(event)   
        self.alarm_event = {}
        
        if self.buffer != '':          
          self.clear_buffer(event)
          self.new_event = True
          alarm_event = Event()
          alarm_event.handle_buffer(self.buffer.split(' '))
          self.is_valid = False

          if alarm_event.is_valid:
            self.is_valid = True            
            self.alarm_event = alarm_event.panel_event            
            alarm_event.is_valid = False          
            #print('Sending valid event')
        else:
          self.is_valid = False
          self.new_event = False  
          

    @classmethod
    def get_buffer(self, event):      
      with open(event.src_path, 'r') as f:
        data = f.readline().strip('\n')         
      return data           
      
    def clear_buffer(self, event):      
      with open(event.src_path, 'w') as f:
        f.write('')        

class Event():  
  
  contact_id = {
        100: {'1': "Emergencia medica"},
        110: {'1': "Alarme de incendio"},
        120: {'1': "Panico"},
        121: {'1': "Ativacao/desativacao sob coacao"},
        122: {'1': "Panico silencioso"},
        130: {
            '1': "Disparo de zona {zone}",
            '3': "Restauracao de zona {zone}"
             },
        133: {'1': "Disparo de zona 24h {zone}"},
        146: {'1': "Disparo silencioso {zone}"},
        301: {
            '1': "Falta de energia AC",
            '3': "Retorno de energia AC"
             },
        342: {
             '1': "Falta de energia AC em componente sem fio {zone}",
             '3': "Retorno energia AC em componente sem fio {zone}"
             },
        302: {
            '1': "Bateria do sistema baixa",
            '3': "Recuperacao bateria do sistema baixa"
             },
        305: {'1': "Reset do sistema"},
        306: {'1': "Alteracao programacao"},
        311: {
            '1': "Bateria ausente",
            '3': "Recuperacao bateria ausente"
             },
        351: {
            '1': "Corte linha telefonica",
            '3': "Restauro linha telefonica"
             },
        354: {'1': "Falha ao comunicar evento"},
        147: {
            '1': "Falha de supervisao {zone}",
            '3': "Recuperacao falha de supervisao {zone}"
             },
        145: {
             '1': "Tamper em dispositivo expansor {zone}",
             '3': "Restauro tamper em dispositivo expansor {zone}"
              },
        383: {
              '1': "Tamper em sensor {zone}",
              '3': "Restauro tamper em sensor {zone}"
              },
        384: {
            '1': "Bateria baixa em componente sem fio {zone}",
            '3': "Recuperacao bateria baixa em componente sem fio {zone}"
             },
        401: {
             '3': "Ativacao manual",
             '1': "Desativacao manual"
             },
        403: {
             '3': "Ativacao automatica",
             '1': "Desativacao automatica"
             },
        404: {
            '3': "Ativacao remota",
            '1': "Desativacao remota",
             },
        407: {
            '3': "Ativacao remota II",
            '1': "Desativacao remota II",
             },
        408: {'1': "Ativacao por uma tecla"},
        410: {'1': "Acesso remoto"},
        461: {'1': "Senha incorreta"},
        570: {
             '1': "Bypass de zona {zone}",
             '3': "Cancel bypass de zona {zone}"
             },
        602: {'1': "Teste periodico"},
        621: {'1': "Reset do buffer de eventos"},
        601: {'1': "Teste manual"},
        616: {'1': "Solicitacao de manutencao"},
        422: {
            '1': "Acionamento de PGM {zone}",
            '3': "Desligamento de PGM {zone}"
             },
        625: {'1': "Data e hora reiniciados"}
    }

  panel_event = ''
  is_valid = False  

  def handle_buffer(self, buffer):
    self.is_valid = self.contactid_is_valid(buffer)

    self.panel_event = {
      'command': 'b0',
      'channel': buffer[0],
      'event': buffer[1],
      #'identifier': '18',
      'qualifier': buffer[2],
      'partition': buffer[3].zfill(2),
      'zone': buffer[4].zfill(3)
    }    

  def contactid_is_valid(self, buffer):    
    buffer_length = len(buffer)    
    if buffer_length != 5:
      return False
    
    try:
      buffer = [int(x) for x in buffer]      
    except:
      return False

    is_valid = {}

    is_valid['channel'] = buffer[0] in [11, 12, 21, 22]
    is_valid['event'] = buffer[1] in self.contact_id
    is_valid['qualifier'] = buffer[2] in [1, 3]    
    is_valid['partition'] = buffer[3] in [*range(0, 100)]
    is_valid['zone'] = buffer[4] in [*range(1, 1000)]

    for item in is_valid:
      if is_valid[item] == False:            
        return False
    return True

  def event_validation(self, event_code):
    return True if event_code in self.contact_id else False    
