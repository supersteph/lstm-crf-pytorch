from utils import *
from embedding import embed
class rnn_crf(nn.Module):
    def __init__(self, char_vocab_size, word_vocab_size, num_tags):
        super().__init__()
        self.rnn = rnn(char_vocab_size, word_vocab_size, num_tags)
        self.crf = crf(num_tags)
        self = self.cuda() if CUDA else self

    def forward(self, xc, xw, y): # for training
        self.zero_grad()
        mask = xw.gt(0).float()
        h = self.rnn(xc, xw, mask)
        h = h.cuda()
        Z = self.crf.forward(h, mask)
        score = self.crf.score(h, y, mask)
        return torch.mean(Z - score) # NLL loss

    def decode(self, xc, xw): # for inference 
        mask = xw.gt(0).float()
        h = self.rnn(xc, xw, mask)
        return self.crf.decode(h, mask)

class rnn(nn.Module):
    def __init__(self, char_vocab_size, word_vocab_size, num_tags):
        super().__init__()

        # architecture
        self.embed = embed(char_vocab_size, word_vocab_size)
        self.rnn = getattr(nn, RNN_TYPE)(
            input_size = sum(EMBED.values()),
            hidden_size = HIDDEN_SIZE // NUM_DIRS,
            num_layers = NUM_LAYERS,
            bias = True,
            batch_first = True,
            dropout = DROPOUT,
            bidirectional = (NUM_DIRS == 2)
        )
        self.out = nn.Linear(HIDDEN_SIZE, num_tags) # RNN output to tag

    def init_state(self): # initialize RNN states
        args = (NUM_LAYERS * NUM_DIRS, BATCH_SIZE, HIDDEN_SIZE // NUM_DIRS)
        hs = zeros(*args) # hidden state
        if RNN_TYPE == "LSTM":
            cs = zeros(*args) # LSTM cell state
            return (hs, cs)
        return hs

    def forward(self, xc, xw, mask):
        s = self.init_state()
        x = self.embed(xc, xw)
        x = nn.utils.rnn.pack_padded_sequence(x, mask.sum(1).int(), batch_first = True)
        h, _ = self.rnn(x, s)
        h, _ = nn.utils.rnn.pad_packed_sequence(h, batch_first = True)
        h = self.out(h)
        h *= mask.unsqueeze(2)
        return h

class crf(nn.Module):
    def __init__(self, num_tags):
        super().__init__()
        self.num_tags = num_tags

        # matrix of transition scores from j to i
        self.trans = nn.Parameter(randn(num_tags, num_tags))
        self.trans.data[SOS_IDX, :] = -10000 # no transition to SOS
        self.trans.data[:, EOS_IDX] = -10000 # no transition from EOS except to PAD
        self.trans.data[:, PAD_IDX] = -10000 # no transition from PAD except to PAD
        self.trans.data[PAD_IDX, :] = -10000 # no transition to PAD except from EOS
        self.trans.data[PAD_IDX, EOS_IDX] = 0
        self.trans.data[PAD_IDX, PAD_IDX] = 0

    def forward(self, h, mask): # forward algorithm
        # initialize forward variables in log space
        score = Tensor(BATCH_SIZE, self.num_tags).fill_(-10000) # [B, C]
        score[:, SOS_IDX] = 0.
        trans = self.trans.unsqueeze(0) # [1, C, C]
        for t in range(h.size(1)): # recursion through the sequence
            mask_t = mask[:, t].unsqueeze(1)
            emit_t = h[:, t].unsqueeze(2) # [B, C, 1]
            score_t = score.unsqueeze(1) + emit_t + trans # [B, 1, C] -> [B, C, C]
            score_t = log_sum_exp(score_t) # [B, C, C] -> [B, C]
            score = score_t * mask_t + score * (1 - mask_t)
        score = log_sum_exp(score + self.trans[EOS_IDX])
        return score # partition function

    def score(self, h, y, mask): # calculate the score of a given sequence
        score = Tensor(BATCH_SIZE).fill_(0.)
        h = h.unsqueeze(3)
        trans = self.trans.unsqueeze(2)
        for t in range(h.size(1)): # recursion through the sequence
            mask_t = mask[:, t]
            emit_t = torch.cat([h[t, y[t + 1]] for h, y in zip(h, y)])
            trans_t = torch.cat([trans[y[t + 1], y[t]] for y in y])
            score += (emit_t + trans_t) * mask_t
        last_tag = y.gather(1, mask.sum(1).long().unsqueeze(1)).squeeze(1)
        score += self.trans[EOS_IDX, last_tag]
        return score

    def decode(self, h, mask): # Viterbi decoding
        # initialize backpointers and viterbi variables in log space
        bptr = LongTensor()
<<<<<<< HEAD
        score = Tensor(BATCH_SIZE, self.num_tags+3).fill_(-10000.)
=======
        score = Tensor(BATCH_SIZE, self.num_tags).fill_(-10000)
        score[:, SOS_IDX] = 0.
>>>>>>> 2b9b8dc49c6566ca377677c752f12a1365181aea

        score[:, SOS_IDX] = 0.
        trans = torch.load("trans.ptb").cuda()
        for t in range(h.size(1)): # recursion through the sequence
            mask_t = mask[:, t].unsqueeze(1)
            score_t = score.unsqueeze(1) + trans # [B, 1, C] -> [B, C, C]
            score_t, bptr_t = score_t.max(2) # best previous scores and tags
            emission = h[:, t]
            ends = torch.tensor([[emission[i][3],emission[i][6],emission[i][3]]for i in range(emission.size()[0])]).cuda()
            score_t += torch.cat((emission,ends),dim=1) # plus emission scores
            #score_t += emission
            bptr = torch.cat((bptr, bptr_t.unsqueeze(1)), 1)
            score = score_t * mask_t + score * (1 - mask_t)
        score += trans[EOS_IDX]
        for i in range(BATCH_SIZE):
            score[i][3] = -10000
        best_score, best_tag = torch.max(score, 1)

        # back-tracking
        bptr = bptr.tolist()
        best_path = [[i] for i in best_tag.tolist()]
        for b in range(BATCH_SIZE):
            x = best_tag[b] # best tag
            y = int(mask[b].sum().item())
            for bptr_t in reversed(bptr[b][:y]):
                x = bptr_t[x]
                best_path[b].append(x)
            if best_path[b][1]==11 and 4 in best_path[b]:
                best_path[b] = [2]
                x=13
                for bptr_t in reversed(bptr[b][:y]):
                    x = bptr_t[x]
                    best_path[b].append(x)
                #print("fuck up")
            best_path[b].pop()
            best_path[b].reverse()
        #print(best_path)
        return best_path

    # def maxwithlimits(bptr, score):
    #     _,best_tag = torch.max(score, 1)
    #     for b in range(BATCH_SIZE):
    #         if best_path == 
