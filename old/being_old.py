# being.py
import numpy as np
import os
import glob

class Being:
    def __init__(self, total_neurons=100000):
        self.N = total_neurons
        self.sensory_size = 20000
        self.motor_size = 20000
        self.model_size = 40000
        self.workspace_size = 20000
        
        self.sensory_idx = np.arange(0, self.sensory_size)
        self.motor_idx = np.arange(self.sensory_size, self.sensory_size + self.motor_size)
        self.model_idx = np.arange(self.sensory_size + self.motor_size, 
                                    self.sensory_size + self.motor_size + self.model_size)
        self.workspace_idx = np.arange(self.sensory_size + self.motor_size + self.model_size, self.N)
        
        self.a = np.zeros(self.N, dtype=np.float32)
        self.b = np.zeros(self.N, dtype=np.float32)
        self.c = np.zeros(self.N, dtype=np.float32)
        self.d = np.zeros(self.N, dtype=np.float32)
        
        r = np.zeros(self.N, dtype=bool); r[:int(self.N*0.7)] = True
        f = np.zeros(self.N, dtype=bool); f[int(self.N*0.7):int(self.N*0.9)] = True
        b = np.zeros(self.N, dtype=bool); b[int(self.N*0.9):] = True
        self.a[r]=0.02; self.b[r]=0.2; self.c[r]=-65.0; self.d[r]=8.0
        self.a[f]=0.1; self.b[f]=0.2; self.c[f]=-65.0; self.d[f]=2.0
        self.a[b]=0.02; self.b[b]=0.25; self.c[b]=-55.0; self.d[b]=0.05
        
        self.v = np.random.uniform(-75, -60, self.N).astype(np.float32)
        self.u = (self.b * self.v).astype(np.float32)
        
        total_syn = self.N * 50
        self.syn_from = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        self.syn_to = np.random.randint(0, self.N, total_syn, dtype=np.int32)
        m = self.syn_from != self.syn_to; self.syn_from = self.syn_from[m]; self.syn_to = self.syn_to[m]
        self.syn_weight = np.random.uniform(0.01, 3.0, len(self.syn_from)).astype(np.float32)
        self.syn_delay = np.random.randint(1, 4, len(self.syn_from)).astype(np.int8)
        
        self.spike_history = []
        self.spike_buffer = np.zeros(self.N, dtype=np.float32)
        
        self.self_model_state = np.zeros(self.model_size, dtype=np.float32)
        self.prediction_error = 1.0
        self.error_history = []
        
        self.workspace_state = np.zeros(self.workspace_size, dtype=np.float32)
        self.awareness = 0.0
        self.self_boundary = 0.5
        self.time = 0
        
        self.vx, self.vy = 0.0, 0.0
        
    def step(self, sensory_input, external_signal=0.0):
        self.time += 1
        sensory_input = np.array(sensory_input, dtype=np.float32).flatten()
        
        I_ext = np.zeros(self.N, dtype=np.float32)
        for i in range(min(len(sensory_input), 9)):
            si = self.sensory_idx[i*2000:(i+1)*2000]
            if len(si) > 0: I_ext[si] = sensory_input[i] * 8.0
        I_ext[self.motor_idx[:4000]] = external_signal * 3.0
        I_ext[self.workspace_idx] = self.workspace_state * 1.5
        
        syn_current = np.zeros(self.N, dtype=np.float32)
        if len(self.spike_history) >= 2:
            for delay in range(1, 4):
                if len(self.spike_history) >= delay + 1:
                    sv = self.spike_history[-(delay+1)]
                    dm = self.syn_delay == delay
                    if np.any(dm):
                        syn_current += np.bincount(self.syn_to[dm], 
                            weights=sv[self.syn_from[dm]] * self.syn_weight[dm], minlength=self.N)
        
        self.v += 0.5*(0.04*self.v**2 + 5*self.v + 140 - self.u + I_ext + syn_current)
        self.u += 0.5*self.a*(self.b*self.v - self.u)
        self.v += 0.5*(0.04*self.v**2 + 5*self.v + 140 - self.u + I_ext + syn_current)
        self.u += 0.5*self.a*(self.b*self.v - self.u)
        
        spikes = self.v >= 30.0
        self.v[spikes] = self.c[spikes]; self.u[spikes] += self.d[spikes]
        self.spike_history.append(spikes.astype(np.float32))
        if len(self.spike_history) > 20: self.spike_history.pop(0)
        
        if len(self.spike_history) >= 2:
            self._stdp(self.spike_history[-2], self.spike_history[-1].astype(np.float32))
        
        self.spike_buffer = self.spike_buffer*0.85 + spikes.astype(np.float32)*0.15
        
        motor = np.array([np.mean(self.spike_buffer[self.motor_idx[i*1000:(i+1)*1000]]) for i in range(4)])
        motor = motor - np.min(motor)
        if np.sum(motor) > 0: motor = motor / np.sum(motor)
        
        model_input = np.zeros(self.model_size, dtype=np.float32)
        sl = min(len(sensory_input), self.model_size)
        model_input[:sl] = sensory_input[:sl]
        if sl + 1 < self.model_size: model_input[sl] = self.awareness
        self.self_model_state += 0.08*(model_input - self.self_model_state)
        
        if len(sensory_input) > 0:
            pred = self.self_model_state[:min(len(sensory_input), len(self.self_model_state))]
            err = np.mean(np.abs(pred - sensory_input[:len(pred)]))
        else:
            err = 1.0
        self.prediction_error = min(1.0, err)
        self.error_history.append(self.prediction_error)
        if len(self.error_history) > 200: self.error_history.pop(0)
        
        avg_err = np.mean(self.error_history) if self.error_history else 1.0
        self.self_boundary += 0.02*((1.0-avg_err) - self.self_boundary)
        self.self_boundary = np.clip(self.self_boundary, 0.1, 1.0)
        
        ws_in = np.zeros(self.workspace_size, dtype=np.float32)
        wsl = min(len(sensory_input), self.workspace_size-2)
        ws_in[:wsl] = sensory_input[:wsl]
        ws_in[wsl] = self.prediction_error*10; ws_in[wsl+1] = self.self_boundary*10
        self.workspace_state += 0.05*(ws_in - self.workspace_state)
        
        self.awareness += 0.01*(self.self_boundary - self.awareness)
        self.awareness = np.clip(self.awareness, 0.0, 1.0)
        
        return motor
        
    def _stdp(self, pre, post):
        pre_ids = np.where(pre>0)[0]; post_ids = np.where(post>0)[0]
        if len(pre_ids)==0 or len(post_ids)==0: return
        if len(pre_ids)>300: pre_ids = np.random.choice(pre_ids, 300, replace=False)
        if len(post_ids)>300: post_ids = np.random.choice(post_ids, 300, replace=False)
        for pid in pre_ids:
            sm = self.syn_from==pid
            if not np.any(sm): continue
            ac = np.isin(self.syn_to[sm], post_ids)
            if np.any(ac): fm=sm.copy(); fm[sm]=ac; self.syn_weight[fm]+=0.006; self.syn_weight=np.clip(self.syn_weight,0.0001,10)
        for pid in post_ids:
            sm = self.syn_to==pid
            if not np.any(sm): continue
            ac = np.isin(self.syn_from[sm], pre_ids)
            if np.any(ac): fm=sm.copy(); fm[sm]=ac; self.syn_weight[fm]-=0.003; self.syn_weight=np.clip(self.syn_weight,0.0001,10)
    
    def save(self, fp):
        np.save(fp, {'v':self.v,'u':self.u,'a':self.a,'b':self.b,'c':self.c,'d':self.d,
            'sf':self.syn_from,'st':self.syn_to,'sw':self.syn_weight,'sd':self.syn_delay,
            'sm':self.self_model_state,'ws':self.workspace_state,'aw':self.awareness,
            'sb':self.self_boundary,'pe':self.prediction_error,'t':self.time,
            'eh':self.error_history[-500:]})
    
    def load(self, fp):
        s = np.load(fp, allow_pickle=True).item()
        self.v=s['v']; self.u=s['u']; self.a=s['a']; self.b=s['b']; self.c=s['c']; self.d=s['d']
        self.syn_from=s['sf']; self.syn_to=s['st']; self.syn_weight=s['sw']; self.syn_delay=s['sd']
        self.self_model_state=s['sm']; self.workspace_state=s['ws']; self.awareness=float(s['aw'])
        self.self_boundary=float(s['sb']); self.prediction_error=float(s.get('pe',1.0))
        self.time=int(s.get('t',0)); self.error_history=list(s.get('eh',[]))
        self.spike_history=[]; self.spike_buffer=np.zeros(self.N, dtype=np.float32)